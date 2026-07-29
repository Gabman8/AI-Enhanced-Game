import threading
import queue
import re
from dataclasses import dataclass
from typing import Optional

try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
except ImportError:
    _LLAMA_AVAILABLE = False
    Llama = None
 
@dataclass
class DialogueContext:
    enemy_type: str
    personality: str
    anger: float
    fear: float
    confidence: float
    category: Optional[str] = None 
 
    @classmethod
    def from_character(cls, character, category=None):
        return cls(
            enemy_type=character.type,
            personality=character.personality,
            anger=character.anger,
            fear=character.fear,
            confidence=character.confidence,
            category=category,
        )
 
# ------------------------------------------------------------------
# 3. Wrapper síncrono del LLM local
# ------------------------------------------------------------------
 
class LocalDialogueLLM:
 
    def __init__(
        self,
        model_path,
        n_ctx=512,
        n_threads=4,
        n_gpu_layers=0,   
        max_tokens=20,
        temperature=0.7,
        cache_size=256,
    ):
        if not _LLAMA_AVAILABLE:
            raise RuntimeError("llama_cpp is not installed")
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._cache = {}
        self._cache_size = cache_size
 
    """def _cache_key(self, ctx: DialogueContext):
        # Redondeamos las emociones para que estados casi idénticos
        # reutilicen la misma frase en vez de generar de nuevo.
        return (
            ctx.enemy_type,
            ctx.category,
            round(ctx.anger, 1),
            round(ctx.fear, 1),
            round(ctx.confidence, 1),
        )"""
 
    def _build_prompt(self, ctx: DialogueContext):
        emotion = (ctx.category or "neutral").lower()
        
        # Tailor tone to current emotion
        if emotion == "afraid":
            tone_desc = "aterrorizado y huyendo desesperadamente, con miedo a morir"
        elif emotion == "angry":
            tone_desc = "furioso y agresivo, cargando al ataque"
        elif emotion == "confident":
            tone_desc = "confiado y dominante, burlándote de tu enemigo"
        elif emotion == "calm":
            tone_desc = "frío y calculador, completamente concentrado"
        else:
            tone_desc = f"{ctx.personality} y listo para pelear"
        
        return (
            f"Eres un guerrero {tone_desc}.\n"
            f"Di UNA frase corta de batalla en ESPAÑOL que refleje tu estado emocional, máximo 8 palabras.\n"
            f"Sin emojis, sin números, solo letras y puntuación básica.\n"
            f"Frase:"
        )
 
    def _clean(self, text):
        text = text.strip().strip('"').strip()
        text = text.split("\n")[0]
        # Keep Spanish characters (accents, ñ) plus basic ASCII
        text = re.sub(r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ.!?\'\-]', '', text)
        words = text.split()
        if len(words) > 10:
            text = " ".join(words[:10])
        return text.strip()
 
    def generate_for_context(self, ctx: DialogueContext) -> str:
        """key = self._cache_key(ctx)
        if key in self._cache:
            return self._cache[key]"""
 
        prompt = self._build_prompt(ctx)
        line = self._generate_raw(prompt)
 
        """if len(self._cache) >= self._cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = line"""
        return line

    def _generate_raw(self, prompt: str) -> str:
        output = self.llm(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stop=["\n"],
        )
        return self._clean(output["choices"][0]["text"])
 
 
# ------------------------------------------------------------------
# 4. Async wrapper, to not interrupt the game loop
# ------------------------------------------------------------------
 
class AsyncDialogueLLM:
    """
    request(character_id, ctx)  -> pide una frase (no bloquea, no devuelve nada)
    poll(character_id)          -> devuelve la frase si ya está lista, o None
 
    Un único hilo de fondo procesa las peticiones en orden, así nunca
    hay dos generaciones compitiendo por CPU a la vez (importante en
    modelos locales sin GPU).
    """
 
    def __init__(self, local_llm: LocalDialogueLLM):
        self.local_llm = local_llm
        self._requests = queue.Queue()
        self._results = {}
        self._results_lock = threading.Lock()
        self._pending = set()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()
 
    def request(self, character_id, ctx):
        # Accept either a DialogueContext dataclass or a plain dict
        if isinstance(ctx, dict):
            ctx = DialogueContext(
                enemy_type=ctx.get("enemy_type", "unknown"),
                personality=ctx.get("personality", "neutral"),
                anger=float(ctx.get("anger", 0.5)),
                fear=float(ctx.get("fear", 0.2)),
                confidence=float(ctx.get("confidence", 0.5)),
                category=ctx.get("category"),
            )
        if character_id in self._pending:
            return
        self._pending.add(character_id)
        self._requests.put((character_id, ctx))
 
    def poll(self, character_id) -> Optional[str]:
        with self._results_lock:
            return self._results.pop(character_id, None)
 
    def _run(self):
        while True:
            character_id, ctx = self._requests.get()
            try:
                line = self.local_llm.generate_for_context(ctx)
            except Exception as exc:
                line = None
                print(f"[AsyncDialogueLLM] error generando frase: {exc}")
            with self._results_lock:
                self._results[character_id] = line
            self._pending.discard(character_id)
 
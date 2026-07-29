import threading
import queue
from dataclasses import dataclass
from typing import Optional
from llama_cpp import Llama
 
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
        temperature=0.5,
        cache_size=256,
    ):
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
        
        tone = (ctx.category or "neutral").replace("_", " ")
        return (
            f"Yoy are a {ctx.personality} person interacting with other in a videogame\n"
            f"Emotional state -> anger: {ctx.anger:.2f}, "
            f"fear: {ctx.fear:.2f}, confidence: {ctx.confidence:.2f}.\n"
            f"Situation tone: {tone}.\n"
            f"Say ONE short battle line, maximum 10 words. "
            f"No quotes, no explanations, no stage directions.\n"
            f"Line:"
        )
 
    def _clean(self, text):
        text = text.strip().strip('"').strip()
        text = text.split("\n")[0]
        words = text.split()
        if len(words) > 12:
            text = " ".join(words[:12])
        return text
 
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
 
    def request(self, character_id, ctx: DialogueContext):
        if character_id in self._pending:
            return  # ya hay una petición en curso para este enemigo, no dupliques
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
 
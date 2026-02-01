"""
title: Scientific Council
author: Carlo
version: 1.0.0
description: Concilio di LLM per libri scientifici: LaTeX, verifiche matematiche, bibliografia, esercizi, grafici multi-dimensionali
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Tuple, Any
import requests
import base64
import io
import json
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Matplotlib per grafici 2D/3D
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Plotly per grafici interattivi
import plotly.graph_objects as go

# NumPy e SymPy per matematica
import numpy as np
import sympy as sp


@dataclass
class ModelConfig:
    """Configurazione per un modello LLM nel concilio."""
    name: str
    weight: float
    specialty: str


class OllamaCouncil:
    """Gestisce la consultazione parallela di più modelli Ollama."""

    # Configurazioni modelli per dominio
    COUNCIL_CONFIGS = {
        "matematica": [
            ModelConfig("qwen2-math", 1.5, "Matematica pura e calcolo simbolico"),
            ModelConfig("qwen2.5", 1.0, "Ragionamento matematico generale"),
            ModelConfig("mistral", 0.8, "Logica e dimostrazione"),
            ModelConfig("gemma2", 0.9, "Analisi matematica"),
        ],
        "codice": [
            ModelConfig("qwen2.5-coder", 1.5, "Programmazione e algoritmi"),
            ModelConfig("codellama", 1.3, "Sviluppo software"),
            ModelConfig("mistral", 0.8, "Analisi codice"),
        ],
        "italiano": [
            ModelConfig("mistral", 1.2, "Lingua italiana e stile"),
            ModelConfig("gemma2", 1.0, "Scrittura scientifica"),
            ModelConfig("llama3", 0.9, "Revisione testi"),
        ],
        "sicurezza": [
            ModelConfig("qwen2.5-coder", 1.2, "Sicurezza informatica"),
            ModelConfig("mistral", 1.0, "Crittografia e vulnerabilità"),
            ModelConfig("codellama", 0.9, "Analisi sicurezza codice"),
        ],
        "generale": [
            ModelConfig("qwen2.5", 1.0, "Conoscenza generale"),
            ModelConfig("mistral", 1.0, "Ragionamento generale"),
            ModelConfig("llama3", 0.9, "Sintesi e analisi"),
            ModelConfig("gemma2", 0.8, "Supporto generale"),
        ],
    }

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Inizializza il concilio LLM."""
        self.ollama_url = ollama_url
        self.available_models = self._get_available_models()

    def _get_available_models(self) -> List[str]:
        """Recupera i modelli disponibili da Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        except Exception as e:
            print(f"⚠️ Errore recupero modelli Ollama: {e}")
            return []

    def _normalize_model_name(self, model_name: str) -> Optional[str]:
        """Trova il modello disponibile che corrisponde al nome base."""
        # Cerca match esatto
        if model_name in self.available_models:
            return model_name

        # Cerca match parziale (es. "qwen2-math" -> "qwen2-math:latest")
        for available in self.available_models:
            if available.startswith(model_name):
                return available
            # Controlla anche senza tag
            base_name = available.split(":")[0]
            if base_name == model_name or base_name.startswith(model_name):
                return available

        return None

    def _query_model(self, config: ModelConfig, prompt: str, timeout: int = 35) -> Dict[str, Any]:
        """Esegue una query a un singolo modello."""
        model_name = self._normalize_model_name(config.name)

        if not model_name:
            return {
                "model": config.name,
                "response": None,
                "error": f"Modello {config.name} non disponibile",
                "weight": config.weight,
                "specialty": config.specialty,
            }

        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                "model": config.name,
                "response": data.get("response", ""),
                "error": None,
                "weight": config.weight,
                "specialty": config.specialty,
            }
        except Exception as e:
            return {
                "model": config.name,
                "response": None,
                "error": str(e),
                "weight": config.weight,
                "specialty": config.specialty,
            }

    def consult_council(self, prompt: str, domain: str = "generale", max_models: int = 5) -> List[Dict[str, Any]]:
        """Consulta il concilio di modelli in parallelo."""
        # Seleziona configurazione per dominio
        configs = self.COUNCIL_CONFIGS.get(domain, self.COUNCIL_CONFIGS["generale"])

        # Filtra solo modelli disponibili
        available_configs = []
        for config in configs[:max_models]:
            if self._normalize_model_name(config.name):
                available_configs.append(config)

        # Fallback se nessun modello configurato è disponibile
        if not available_configs and self.available_models:
            print(f"⚠️ Nessun modello configurato disponibile per '{domain}', uso fallback")
            for model in self.available_models[:3]:
                available_configs.append(ModelConfig(model.split(":")[0], 1.0, "Modello generico"))

        if not available_configs:
            return []

        # Query parallele
        responses = []
        with ThreadPoolExecutor(max_workers=min(5, len(available_configs))) as executor:
            future_to_config = {
                executor.submit(self._query_model, config, prompt): config
                for config in available_configs
            }

            for future in as_completed(future_to_config):
                try:
                    result = future.result(timeout=40)
                    if result["response"]:  # Includi solo risposte successful
                        responses.append(result)
                except Exception as e:
                    config = future_to_config[future]
                    print(f"⚠️ Timeout/errore per {config.name}: {e}")

        # Ordina per peso
        responses.sort(key=lambda x: x["weight"], reverse=True)
        return responses


class ResponseAggregator:
    """Aggrega e analizza le risposte di più modelli."""

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcola similarità Jaccard tra due testi."""
        if not text1 or not text2:
            return 0.0

        # Normalizza e tokenizza
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 or not words2:
            return 0.0

        # Jaccard index
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def detect_consensus(self, responses: List[Dict[str, Any]], threshold: float = 0.6) -> Dict[str, Any]:
        """Identifica consenso tra le risposte."""
        if not responses:
            return {"has_consensus": False, "majority_group": [], "agreement": 0.0}

        n = len(responses)
        if n == 1:
            return {"has_consensus": True, "majority_group": [0], "agreement": 1.0}

        # Calcola matrice di similarità
        similarity_matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                else:
                    sim = self.calculate_similarity(
                        responses[i]["response"],
                        responses[j]["response"]
                    )
                    row.append(sim)
            similarity_matrix.append(row)

        # Clustering semplice: trova gruppo con più membri simili
        groups = []
        assigned = [False] * n

        for i in range(n):
            if assigned[i]:
                continue

            group = [i]
            assigned[i] = True

            for j in range(i + 1, n):
                if assigned[j]:
                    continue

                # Verifica se j è simile al gruppo
                avg_sim = sum(similarity_matrix[i][j] for i in group) / len(group)
                if avg_sim >= threshold:
                    group.append(j)
                    assigned[j] = True

            groups.append(group)

        # Trova gruppo maggioritario
        majority_group = max(groups, key=len)
        agreement = len(majority_group) / n

        return {
            "has_consensus": agreement >= 0.5,
            "majority_group": majority_group,
            "agreement": agreement,
            "num_groups": len(groups),
        }

    def weighted_aggregation(self, responses: List[Dict[str, Any]]) -> str:
        """Aggregazione pesata: presenta risposta primaria + alternative."""
        if not responses:
            return "❌ Nessuna risposta disponibile."

        output = []

        # Risposta primaria (peso maggiore)
        primary = responses[0]
        output.append(f"### 🎯 Risposta Principale ({primary['model']})\n")
        output.append(f"**Specialità:** {primary['specialty']} | **Peso:** {primary['weight']}\n")
        output.append(f"{primary['response']}\n")

        # Opinioni alternative
        if len(responses) > 1:
            output.append(f"\n### 💭 Opinioni Alternative\n")
            for i, resp in enumerate(responses[1:], 1):
                output.append(f"**{i}. {resp['model']}** (Peso: {resp['weight']}) - {resp['specialty']}\n")
                # Mostra sintesi o primi 200 caratteri
                preview = resp['response'][:200] + "..." if len(resp['response']) > 200 else resp['response']
                output.append(f"{preview}\n")

        return "\n".join(output)

    def comparative_analysis(self, responses: List[Dict[str, Any]]) -> str:
        """Analisi comparativa con consenso e divergenze."""
        if not responses:
            return "❌ Nessuna risposta disponibile."

        output = []

        # Analisi consenso
        consensus = self.detect_consensus(responses)

        output.append(f"### 📊 Analisi Comparativa\n")
        output.append(f"**Modelli consultati:** {len(responses)}\n")
        output.append(f"**Livello di consenso:** {consensus['agreement']:.0%}\n")
        output.append(f"**Gruppi di opinione:** {consensus['num_groups']}\n\n")

        if consensus["has_consensus"]:
            output.append(f"✅ **Consenso raggiunto** tra {len(consensus['majority_group'])} modelli\n\n")
            output.append(f"### 🎯 Posizione di Maggioranza\n")
            for idx in consensus["majority_group"]:
                resp = responses[idx]
                output.append(f"**{resp['model']}** ({resp['specialty']})\n")

            # Mostra risposta rappresentativa (primo del gruppo)
            representative = responses[consensus["majority_group"][0]]
            output.append(f"\n{representative['response']}\n")
        else:
            output.append(f"⚠️ **Opinioni divergenti** - Nessun consenso chiaro\n\n")

        # Mostra tutte le risposte
        output.append(f"\n### 📝 Tutte le Risposte\n")
        for i, resp in enumerate(responses, 1):
            in_majority = i - 1 in consensus.get("majority_group", [])
            marker = "✓" if in_majority else "○"
            output.append(f"\n{marker} **{i}. {resp['model']}** - {resp['specialty']} (Peso: {resp['weight']})\n")
            output.append(f"{resp['response']}\n")

        return "\n".join(output)

    def synthesis(self, responses: List[Dict[str, Any]], council: 'OllamaCouncil') -> str:
        """Sintesi unificata usando un LLM aggiuntivo."""
        if not responses:
            return "❌ Nessuna risposta disponibile."

        # Costruisci prompt per sintesi
        synthesis_prompt = "Sintetizza le seguenti risposte di diversi modelli LLM in una risposta unificata, evidenziando i punti di accordo e disaccordo:\n\n"

        for i, resp in enumerate(responses, 1):
            synthesis_prompt += f"--- Risposta {i} ({resp['model']}) ---\n{resp['response']}\n\n"

        synthesis_prompt += "\nFornisci una sintesi coerente che integri tutti i punti di vista."

        # Usa il modello con peso maggiore per la sintesi
        best_model = responses[0]
        config = ModelConfig(best_model["model"], best_model["weight"], "Sintesi")

        result = council._query_model(config, synthesis_prompt, timeout=40)

        if result["response"]:
            output = []
            output.append(f"### 🔄 Sintesi Unificata\n")
            output.append(f"**Sintetizzato da:** {result['model']}\n")
            output.append(f"**Basato su:** {len(responses)} modelli\n\n")
            output.append(result["response"])
            return "\n".join(output)
        else:
            # Fallback a weighted
            return self.weighted_aggregation(responses)


class VisualizationHelper:
    """Helper per visualizzazioni matematiche e LaTeX."""

    def fig_to_base64(self, fig, max_base64_length: int = 40000) -> str:
        """
        Converte figura matplotlib in Base64 con compressione adattiva.

        Se l'immagine è troppo grande, riduce qualità/dimensioni per evitare
        il bug del loop ciclico di Open WebUI.
        """
        # Prima prova: PNG a bassa risoluzione
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=72, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        img_bytes = buf.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        plt.close(fig)

        # Se troppo grande, comprimi in JPEG
        if len(img_base64) > max_base64_length:
            try:
                from PIL import Image

                # Riapri come PIL Image
                buf.seek(0)
                img = Image.open(io.BytesIO(img_bytes))

                # Ridimensiona se necessario
                max_dim = 600
                if max(img.size) > max_dim:
                    ratio = max_dim / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.LANCZOS)

                # Converti in RGB e comprimi come JPEG
                if img.mode in ('RGBA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img)
                    img = background

                jpeg_buf = io.BytesIO()
                img.save(jpeg_buf, format='JPEG', quality=60, optimize=True)
                jpeg_buf.seek(0)
                img_base64 = base64.b64encode(jpeg_buf.read()).decode('utf-8')

                return f"data:image/jpeg;base64,{img_base64}"

            except ImportError:
                # Pillow non disponibile, restituisci PNG comunque
                pass

        return f"data:image/png;base64,{img_base64}"

    def create_2d_plot(self, expr_str: str, x_range: Tuple[float, float]) -> str:
        """Crea grafico 2D da espressione sympy."""
        try:
            x = sp.Symbol('x')
            expr = sp.sympify(expr_str)

            # Converti in funzione numpy
            f = sp.lambdify(x, expr, modules=['numpy'])

            # Genera punti
            x_vals = np.linspace(x_range[0], x_range[1], 500)
            y_vals = f(x_vals)

            # Crea plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x_vals, y_vals, linewidth=2)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linewidth=0.5)
            ax.axvline(x=0, color='k', linewidth=0.5)
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('f(x)', fontsize=12)
            ax.set_title(f'$f(x) = {sp.latex(expr)}$', fontsize=14)

            return self.fig_to_base64(fig)

        except Exception as e:
            raise ValueError(f"Errore creazione grafico 2D: {e}\n\nSuggerimenti:\n- Usa sintassi sympy: x**2, sin(x), sqrt(x)\n- Verifica parentesi bilanciate")

    def create_3d_surface(self, expr_str: str, x_range: Tuple[float, float], y_range: Tuple[float, float]) -> str:
        """Crea superficie 3D matplotlib."""
        try:
            x, y = sp.symbols('x y')
            expr = sp.sympify(expr_str)

            # Converti in funzione numpy
            f = sp.lambdify((x, y), expr, modules=['numpy'])

            # Genera meshgrid
            x_vals = np.linspace(x_range[0], x_range[1], 50)
            y_vals = np.linspace(y_range[0], y_range[1], 50)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = f(X, Y)

            # Crea plot 3D
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax.set_xlabel('x', fontsize=10)
            ax.set_ylabel('y', fontsize=10)
            ax.set_zlabel('z', fontsize=10)
            ax.set_title(f'$z = {sp.latex(expr)}$', fontsize=12)
            fig.colorbar(surf, shrink=0.5)

            return self.fig_to_base64(fig)

        except Exception as e:
            raise ValueError(f"Errore creazione superficie 3D: {e}\n\nSuggerimenti:\n- Usa sintassi sympy con x e y: x**2 + y**2, sin(x)*cos(y)\n- Verifica parentesi bilanciate")

    def create_interactive_3d(self, expr_str: str, x_range: Tuple[float, float], y_range: Tuple[float, float]) -> str:
        """Crea superficie 3D interattiva con Plotly."""
        try:
            x, y = sp.symbols('x y')
            expr = sp.sympify(expr_str)

            # Converti in funzione numpy
            f = sp.lambdify((x, y), expr, modules=['numpy'])

            # Genera meshgrid
            x_vals = np.linspace(x_range[0], x_range[1], 50)
            y_vals = np.linspace(y_range[0], y_range[1], 50)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = f(X, Y)

            # Crea grafico Plotly
            fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
            fig.update_layout(
                title=f'z = {expr_str}',
                scene=dict(
                    xaxis_title='x',
                    yaxis_title='y',
                    zaxis_title='z',
                ),
                width=800,
                height=600,
            )

            # Converti in HTML
            html = fig.to_html(include_plotlyjs='cdn', div_id='plotly_graph')
            return html

        except Exception as e:
            raise ValueError(f"Errore creazione grafico 3D interattivo: {e}")

    def latex_to_mathjax(self, latex_code: str) -> str:
        """Wrappa codice LaTeX per rendering MathJax."""
        latex_code = latex_code.strip()

        # Se già wrapped, ritorna così
        if latex_code.startswith('$$') and latex_code.endswith('$$'):
            return latex_code
        if latex_code.startswith('$') and latex_code.endswith('$'):
            return latex_code

        # Wrappa in display mode
        return f"$${latex_code}$$"

    def validate_latex(self, latex_code: str) -> Tuple[bool, str]:
        """Valida sintassi LaTeX base."""
        errors = []

        # Controlla parentesi bilanciate
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        for char in latex_code:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack or brackets[stack[-1]] != char:
                    errors.append(f"Parentesi non bilanciate: {char}")
                else:
                    stack.pop()

        if stack:
            errors.append(f"Parentesi aperte non chiuse: {stack}")

        # Controlla \begin{} e \end{} matching
        begin_pattern = r'\\begin\{([^}]+)\}'
        end_pattern = r'\\end\{([^}]+)\}'

        begins = re.findall(begin_pattern, latex_code)
        ends = re.findall(end_pattern, latex_code)

        if begins != ends:
            errors.append(f"Environments non bilanciati: begin{{{begins}}} vs end{{{ends}}}")

        is_valid = len(errors) == 0
        message = "✅ Sintassi LaTeX valida" if is_valid else f"⚠️ Possibili errori:\n" + "\n".join(f"- {e}" for e in errors)

        return is_valid, message


class Tools:
    """Tool principale per Open WebUI."""

    class Valves(BaseModel):
        """Configurazioni opzionali."""
        OLLAMA_URL: str = Field(
            default="http://localhost:11434",
            description="URL del server Ollama"
        )
        DEFAULT_TIMEOUT: int = Field(
            default=35,
            description="Timeout default per query LLM (secondi)"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.council = OllamaCouncil(self.valves.OLLAMA_URL)
        self.aggregator = ResponseAggregator()
        self.viz = VisualizationHelper()

    def consult_council(
        self,
        domanda: str,
        dominio: str = "generale",
        strategia: str = "weighted"
    ) -> str:
        """
        Consulta il concilio di LLM su una domanda.

        Args:
            domanda: Domanda da sottoporre al concilio
            dominio: Uno tra: matematica, codice, italiano, sicurezza, generale
            strategia: Uno tra: weighted, comparative, synthesis

        Returns:
            Risposta aggregata in formato markdown
        """
        # Valida parametri
        valid_domains = ["matematica", "codice", "italiano", "sicurezza", "generale"]
        valid_strategies = ["weighted", "comparative", "synthesis"]

        if dominio not in valid_domains:
            return f"❌ Dominio non valido. Scegli tra: {', '.join(valid_domains)}"

        if strategia not in valid_strategies:
            return f"❌ Strategia non valida. Scegli tra: {', '.join(valid_strategies)}"

        # Verifica disponibilità modelli
        if not self.council.available_models:
            return """❌ **Errore Consultazione Concilio**

Nessun modello Ollama disponibile.

**Suggerimenti:**
1. Verifica Ollama: `curl http://localhost:11434/api/tags`
2. Scarica modelli: `docker exec -it ollama ollama pull mistral`
3. Modelli consigliati per {dominio}:
   - matematica: qwen2-math, qwen2.5, mistral
   - codice: qwen2.5-coder, codellama
   - italiano: mistral, gemma2
   - sicurezza: qwen2.5-coder, mistral
   - generale: qwen2.5, mistral, llama3
"""

        # Consulta concilio
        responses = self.council.consult_council(domanda, dominio)

        if not responses:
            return f"""⚠️ **Nessuna risposta ottenuta**

Modelli disponibili: {len(self.council.available_models)}
Domini richiesto: {dominio}

Verifica che almeno un modello sia scaricato e funzionante."""

        # Aggrega secondo strategia
        if strategia == "weighted":
            aggregated = self.aggregator.weighted_aggregation(responses)
        elif strategia == "comparative":
            aggregated = self.aggregator.comparative_analysis(responses)
        elif strategia == "synthesis":
            aggregated = self.aggregator.synthesis(responses, self.council)
        else:
            aggregated = self.aggregator.weighted_aggregation(responses)

        # Costruisci output finale
        consensus = self.aggregator.detect_consensus(responses)
        consensus_marker = "✅" if consensus["has_consensus"] else "⚠️"

        output = f"""# 🧠 Concilio di LLM: {dominio.upper()}

**Domanda:** {domanda}
**Modelli consultati:** {len(responses)}
**Strategia:** {strategia}

---

{aggregated}

---
**Consenso:** {consensus_marker} {consensus['agreement']:.0%} ({len(consensus.get('majority_group', []))} modelli su {len(responses)})
"""

        return output

    def generate_latex_formula(
        self,
        descrizione: str,
        tipo: str = "display",
        verifica: bool = True
    ) -> str:
        """
        Genera formula LaTeX da descrizione in linguaggio naturale.

        Args:
            descrizione: Descrizione matematica in italiano
            tipo: Tipo di formula - inline ($...$), display ($$...$$), equation, align
            verifica: Valida sintassi LaTeX

        Returns:
            Codice LaTeX + rendering MathJax
        """
        valid_types = ["inline", "display", "equation", "align"]
        if tipo not in valid_types:
            return f"❌ Tipo non valido. Scegli tra: {', '.join(valid_types)}"

        # Prompt specializzato per LaTeX
        prompt = f"""Genera il codice LaTeX per la seguente espressione matematica.

Descrizione: {descrizione}

ISTRUZIONI CRITICHE:
1. Fornisci SOLO il codice LaTeX puro, senza spiegazioni
2. NON usare markdown (no ```latex, no backticks)
3. NON includere $ o $$ wrapper (saranno aggiunti dopo)
4. Per equation/align, includi \\begin{{}}...\\end{{}}
5. Usa comandi LaTeX standard: \\frac, \\int, \\sum, \\sqrt, ecc.

Esempio output corretto:
\\int_0^1 x^2 \\, dx = \\frac{{1}}{{3}}
"""

        # Consulta concilio matematica
        responses = self.council.consult_council(prompt, "matematica")

        if not responses:
            return "❌ Nessun modello disponibile per generazione LaTeX."

        # Usa risposta del modello con peso maggiore
        latex_raw = responses[0]["response"].strip()

        # Pulizia: rimuovi markdown code blocks
        latex_raw = re.sub(r'```latex\n?', '', latex_raw)
        latex_raw = re.sub(r'```\n?', '', latex_raw)
        latex_raw = re.sub(r'^`|`$', '', latex_raw)
        latex_raw = latex_raw.strip()

        # Formatta secondo tipo
        if tipo == "inline":
            latex_formatted = f"${latex_raw}$"
        elif tipo == "display":
            latex_formatted = f"$${latex_raw}$$"
        elif tipo == "equation":
            if not latex_raw.startswith("\\begin{equation}"):
                latex_formatted = f"\\begin{{equation}}\n{latex_raw}\n\\end{{equation}}"
            else:
                latex_formatted = latex_raw
        elif tipo == "align":
            if not latex_raw.startswith("\\begin{align}"):
                latex_formatted = f"\\begin{{align}}\n{latex_raw}\n\\end{{align}}"
            else:
                latex_formatted = latex_raw
        else:
            latex_formatted = f"$${latex_raw}$$"

        # Validazione
        validation_msg = ""
        if verifica:
            is_valid, msg = self.viz.validate_latex(latex_raw)
            validation_msg = f"\n**Validazione:** {msg}\n"

        output = f"""📐 **Formula LaTeX Generata**

**Descrizione:** {descrizione}
**Tipo:** {tipo}
**Modello:** {responses[0]['model']}

**Codice LaTeX:**
```latex
{latex_raw}
```

**Rendering MathJax:**

{latex_formatted}
{validation_msg}
---
**Nota:** Copia il codice LaTeX per usarlo in documenti scientifici.
"""

        return output

    def verify_proof(
        self,
        teorema: str,
        dimostrazione: str,
        livello_rigore: str = "alto"
    ) -> str:
        """
        Verifica rigorosità di una dimostrazione matematica.

        Args:
            teorema: Enunciato del teorema
            dimostrazione: Dimostrazione da verificare
            livello_rigore: basso, medio, alto

        Returns:
            Analisi multi-modello della dimostrazione
        """
        valid_levels = ["basso", "medio", "alto"]
        if livello_rigore not in valid_levels:
            return f"❌ Livello rigore non valido. Scegli tra: {', '.join(valid_levels)}"

        # Descrizione livelli di rigore
        rigore_desc = {
            "basso": "Verifica logica di base, accetta intuizioni ragionevoli",
            "medio": "Richiede giustificazione di passaggi chiave, identifica gap evidenti",
            "alto": "Standard formale rigoroso, richiede tutti i dettagli, identifica ogni assunzione"
        }

        # Prompt specializzato per verifica
        prompt = f"""Sei un matematico esperto. Verifica la seguente dimostrazione con rigore {livello_rigore}.

**TEOREMA:**
{teorema}

**DIMOSTRAZIONE:**
{dimostrazione}

**LIVELLO DI RIGORE:** {livello_rigore} - {rigore_desc[livello_rigore]}

**ANALISI RICHIESTA:**
1. **Correttezza logica:** Ogni passaggio è giustificato?
2. **Gap nella dimostrazione:** Ci sono salti logici?
3. **Assunzioni implicite:** Quali assunzioni vengono fatte senza dichiararle?
4. **Completezza:** La dimostrazione copre tutti i casi?
5. **Voto finale:** VALIDA / VALIDA CON RISERVE / INVALIDA

Fornisci un'analisi dettagliata punto per punto.
"""

        # Consulta concilio matematica
        responses = self.council.consult_council(prompt, "matematica")

        if not responses:
            return "❌ Nessun modello disponibile per verifica dimostrazione."

        # Presenta tutte le valutazioni
        output = [f"""🔬 **Verifica Dimostrazione Matematica**

**Teorema:** {teorema}

**Livello di rigore:** {livello_rigore} - {rigore_desc[livello_rigore]}

**Modelli consultati:** {len(responses)}

---
"""]

        for i, resp in enumerate(responses, 1):
            output.append(f"""### Valutazione {i}: {resp['model']}
**Specialità:** {resp['specialty']} | **Affidabilità:** {resp['weight']}

{resp['response']}

---
""")

        # Analisi consenso
        consensus = self.aggregator.detect_consensus(responses)
        if consensus["has_consensus"]:
            output.append(f"\n✅ **Consenso raggiunto** tra {len(consensus['majority_group'])} modelli ({consensus['agreement']:.0%})\n")
        else:
            output.append(f"\n⚠️ **Opinioni divergenti** - Consenso: {consensus['agreement']:.0%}\n")

        return "\n".join(output)

    def generate_bibliography(
        self,
        argomento: str,
        stile: str = "bibtex",
        numero: int = 5
    ) -> str:
        """
        Genera bibliografia scientifica.

        Args:
            argomento: Argomento di ricerca
            stile: Formato - bibtex, apa, ieee, chicago
            numero: Numero di riferimenti (1-10)

        Returns:
            Bibliografia formattata
        """
        valid_styles = ["bibtex", "apa", "ieee", "chicago"]
        if stile not in valid_styles:
            return f"❌ Stile non valido. Scegli tra: {', '.join(valid_styles)}"

        if not (1 <= numero <= 10):
            return "❌ Numero riferimenti deve essere tra 1 e 10."

        # Prompt specializzato per bibliografia
        prompt = f"""Genera {numero} riferimenti bibliografici autorevoli per il seguente argomento.

**Argomento:** {argomento}
**Formato richiesto:** {stile.upper()}
**Numero di riferimenti:** {numero}

**ISTRUZIONI:**
1. Seleziona fonti autorevoli: paper peer-reviewed, libri accademici, riviste scientifiche
2. Priorità a pubblicazioni recenti (ultimi 10 anni) ma includi classici fondamentali
3. Varia le tipologie: articoli, libri, conference papers
4. Formatta ESATTAMENTE secondo lo standard {stile.upper()}
5. Includi tutti i campi necessari: autori, titolo, anno, editore/rivista, DOI se disponibile

Fornisci SOLO la bibliografia formattata, senza spiegazioni aggiuntive.
"""

        # Consulta concilio generale
        responses = self.council.consult_council(prompt, "generale")

        if not responses:
            return "❌ Nessun modello disponibile per generazione bibliografia."

        # Usa modello con peso maggiore
        bibliografia = responses[0]["response"]

        output = f"""📚 **Bibliografia Scientifica**

**Argomento:** {argomento}
**Formato:** {stile.upper()}
**Riferimenti:** {numero}
**Generato da:** {responses[0]['model']}

---

{bibliografia}

---

**Note:**
- ⚠️ Verifica citazioni su Google Scholar, arXiv, IEEE Xplore, SpringerLink
- Alcuni riferimenti potrebbero richiedere aggiornamenti (DOI, pagine)
- Per BibTeX: copia nel file .bib e compila con LaTeX
- Per APA/IEEE/Chicago: usa direttamente nel documento
"""

        return output

    def create_exercises(
        self,
        argomento: str,
        numero: int = 5,
        difficolta: str = "medio",
        con_soluzioni: bool = True,
        con_hint: bool = False
    ) -> str:
        """
        Genera esercizi matematici con soluzioni e hint.

        Args:
            argomento: Argomento matematico
            numero: Numero di esercizi (1-10)
            difficolta: facile, medio, difficile, misto
            con_soluzioni: Includi soluzioni step-by-step
            con_hint: Includi suggerimenti progressivi

        Returns:
            Esercizi formattati in markdown con LaTeX
        """
        valid_difficulties = ["facile", "medio", "difficile", "misto"]
        if difficolta not in valid_difficulties:
            return f"❌ Difficoltà non valida. Scegli tra: {', '.join(valid_difficulties)}"

        if not (1 <= numero <= 10):
            return "❌ Numero esercizi deve essere tra 1 e 10."

        # Prompt specializzato per esercizi
        prompt = f"""Genera {numero} esercizi di matematica sul seguente argomento.

**Argomento:** {argomento}
**Difficoltà:** {difficolta}
**Numero esercizi:** {numero}
**Soluzioni:** {'SI' if con_soluzioni else 'NO'}
**Hint:** {'SI' if con_hint else 'NO'}

**ISTRUZIONI:**
1. Crea esercizi progressivi che coprono aspetti diversi dell'argomento
2. Usa LaTeX per formule matematiche (inline $...$ o display $$...$$)
3. Per difficoltà "misto": varia da facile a difficile
4. Formato per ogni esercizio:

   **Esercizio N:** [testo]

   {'''**Hint:** [suggerimenti progressivi]''' if con_hint else ''}

   {'''**Soluzione:**
   *Passo 1:* [spiegazione]
   *Passo 2:* [spiegazione]
   ...
   *Risposta finale:* [risultato]''' if con_soluzioni else ''}

5. Numera gli esercizi chiaramente
6. Rendi le soluzioni dettagliate e didattiche

Fornisci SOLO gli esercizi formattati, senza introduzioni.
"""

        # Consulta concilio matematica
        responses = self.council.consult_council(prompt, "matematica")

        if not responses:
            return "❌ Nessun modello disponibile per generazione esercizi."

        # Usa modello con peso maggiore per consistenza
        esercizi = responses[0]["response"]

        output = f"""✏️ **Esercizi: {argomento}**

**Numero:** {numero} | **Difficoltà:** {difficolta} | **Soluzioni:** {'SI' if con_soluzioni else 'NO'} | **Hint:** {'SI' if con_hint else 'NO'}
**Generato da:** {responses[0]['model']}

---

{esercizi}

---

**Suggerimento didattico:**
- Prima prova a risolvere senza guardare hint/soluzioni
- Usa gli hint se ti blocchi
- Confronta il tuo procedimento con la soluzione step-by-step
"""

        return output

    def plot_mathematical(
        self,
        espressione: str,
        tipo: str = "2d",
        range_x: str = "-10,10",
        range_y: str = "-10,10",
        interattivo: bool = False
    ) -> str:
        """
        Crea visualizzazioni matematiche 2D/3D.

        Args:
            espressione: Espressione matematica (sintassi sympy)
            tipo: 2d, 3d
            range_x: Range x come "min,max" (es. "-5,5")
            range_y: Range y per 3D (es. "-5,5")
            interattivo: Usa Plotly (solo per 3D)

        Returns:
            Grafico in Base64 o HTML embed
        """
        valid_types = ["2d", "3d"]
        if tipo not in valid_types:
            return f"❌ Tipo non valido. Scegli tra: {', '.join(valid_types)}"

        # Parse range
        try:
            x_min, x_max = map(float, range_x.split(','))
            x_range_tuple = (x_min, x_max)
        except:
            return f"❌ Range X non valido. Usa formato: 'min,max' (es. '-10,10')"

        if tipo == "3d":
            try:
                y_min, y_max = map(float, range_y.split(','))
                y_range_tuple = (y_min, y_max)
            except:
                return f"❌ Range Y non valido. Usa formato: 'min,max' (es. '-10,10')"

        # Genera grafico
        try:
            if tipo == "2d":
                img_base64 = self.viz.create_2d_plot(espressione, x_range_tuple)

                # Usa HTML img tag invece di markdown per evitare bug rendering
                output = f"""📊 **Visualizzazione Matematica 2D**

**Espressione:** `{espressione}`
**Range X:** {range_x}

---

<img src="{img_base64}" alt="Grafico 2D" style="max-width:100%; height:auto;">

---

**Note:**
- Sintassi sympy: `x**2` (potenza), `sin(x)`, `cos(x)`, `sqrt(x)`, `exp(x)`, `log(x)`
- Operazioni: `+`, `-`, `*`, `/`, `**` (potenza)
- Costanti: `pi`, `E` (numero di Eulero)
- Esempi: `sin(x) + cos(2*x)`, `x**3 - 2*x + 1`, `exp(-x**2)`
"""
                return output

            elif tipo == "3d":
                if interattivo:
                    # Plotly HTML
                    html_embed = self.viz.create_interactive_3d(espressione, x_range_tuple, y_range_tuple)

                    output = f"""📊 **Visualizzazione Matematica 3D Interattiva**

**Espressione:** `{espressione}`
**Range X:** {range_x} | **Range Y:** {range_y}

---

{html_embed}

---

**Note:**
- Grafico interattivo: ruota, zoom, pan
- Sintassi sympy con x e y: `x**2 + y**2`, `sin(x)*cos(y)`, `sin(sqrt(x**2 + y**2))`
"""
                    return output
                else:
                    # Matplotlib Base64
                    img_base64 = self.viz.create_3d_surface(espressione, x_range_tuple, y_range_tuple)

                    # Usa HTML img tag invece di markdown per evitare bug rendering
                    output = f"""📊 **Visualizzazione Matematica 3D**

**Espressione:** `{espressione}`
**Range X:** {range_x} | **Range Y:** {range_y}

---

<img src="{img_base64}" alt="Grafico 3D" style="max-width:100%; height:auto;">

---

**Note:**
- Sintassi sympy con x e y: `x**2 + y**2`, `sin(x)*cos(y)`, `sin(sqrt(x**2 + y**2))`
- Per grafico interattivo, imposta `interattivo=true`
- Esempi: `x**2 - y**2` (sella), `sin(sqrt(x**2 + y**2))` (ondulazione radiale)
"""
                    return output

        except ValueError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"""❌ **Errore Generazione Grafico**

{str(e)}

**Suggerimenti:**
- Verifica sintassi sympy
- Per 2D: usa solo variabile `x`
- Per 3D: usa variabili `x` e `y`
- Esempi validi:
  - 2D: `sin(x)`, `x**3 - 2*x`, `exp(-x**2/2)`
  - 3D: `x**2 + y**2`, `sin(x)*cos(y)`, `exp(-(x**2 + y**2))`
"""

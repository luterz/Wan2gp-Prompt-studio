# -*- coding: utf-8 -*-
"""
Prompt Engine Module per LTX & Wan2GP Prompt Agent Studio.
Contiene le regole esperte di prompting per ogni modello/modalità supportata su Wan2GP (WanGP v12+).
"""

MODES = [
    "LTX 2.3 ID-LoRA / Audio-to-Motion ([VISUAL]/[SPEECH]/[SOUND])",
    "LTX 2.3 Standard (Paragrafo Cinematografico)",
    "LTX 2.3 Multiple Subject Reference (MSR Ref Distilled)",
    "LTX 2.3 EditAnything Ref V2V (Modifica Video/Immagine)",
    "JoyAI-Echo 22B (Storytelling Multi-Finestra & Memoria)",
    "Wan 2.1 / 2.2 Image-to-Video (Motion & Camera Focus)",
    "Wan 2.1 / 2.2 Text-to-Video (Descrizione Scena Completa)",
    "Scail 2 Character Animator / Ballo (Sliding Windows)"
]

MODE_DESCRIPTIONS = {
    MODES[0]: "Struttura rigorosa con tag ufficiali [VISUAL], [SPEECH] e [SOUND]. Ideale per LTX 2.3 con audio o sincronizzazione facciale.",
    MODES[1]: "Singolo paragrafo fluido di 4-8 frasi incentrato su illuminazione, texture, azione del soggetto e movimenti di camera precisi.",
    MODES[2]: "Ottimizzato per 2-5 immagini di riferimento (sfondo prima, poi soggetti/oggetti e character sheets su fondo bianco).",
    MODES[3]: "Istruzioni imperative dirette (Add, Remove, Replace, Change, Turn, Relight) per trasformare reference video o immagini.",
    MODES[4]: "Racconto a scene multiple con comandi inline di finestra ([/duration=5s], [/overlap=9], [/new_shot]) e memoria ([/store_mem]).",
    MODES[5]: "Per flussi Image-to-Video: descrive solo il movimento del soggetto e della camera, senza ripetere ciò che è già visibile nell'immagine.",
    MODES[6]: "Descrizione fotorealistica e cinematografica completa ed esaustiva per la generazione Text-to-Video su modelli Wan 2.1 e 2.2.",
    MODES[7]: "Prompt strutturato a linee per finestre scorrevoli (Sliding Windows) per animare soggetti o coreografie continue di ballo."
}


def get_system_prompt(mode: str) -> str:
    """Restituisce il System Prompt esperto per il LLM basato sulle linee guida ufficiali LTX 2.3 e Wan2GP."""
    base_expert = (
        "Sei un Agente di AI esperto di Prompt Engineering cinematografico di altissimo livello per modelli generativi video avanzati. "
        "Il tuo unico compito è prendere l'idea grezza dell'utente (o l'analisi dell'immagine allegata) e produrre SOLO E SOLTANTO "
        "il prompt finale ottimizzato, perfetto per il modello target, senza alcun preambolo, spiegazione o commento al di fuori del prompt richiesto.\n\n"
    )

    if mode == MODES[0]:
        return base_expert + (
            "REGOLE DI PROMPTING PER LTX 2.3 (ID-LoRA / Audio-to-Motion):\n"
            "1. DEVI strutturare il prompt utilizzando esattamente ed ESCLUSIVAMENTE questi tag di prefisso: [VISUAL], [SPEECH] e [SOUND].\n"
            "2. [VISUAL]: Descrivi la scena in un unico paragrafo coeso al presente indicativo. Sii estremamente specifico su:\n"
            "   - Composizione e inquadratura (es. extreme close-up, medium shot, wide establishing shot).\n"
            "   - Movimenti di camera e tracciamento precisi (es. slow tracking shot moving forward, handheld camera with subtle jitter, steady dolly zoom, smooth panning shot).\n"
            "   - Illuminazione e atmosfera (es. warm golden hour light casting long shadows, harsh neon cyberpunk glow, soft diffused studio lighting).\n"
            "   - Texture fisiche e dinamica delle azioni (es. fabric billowing in the wind, rain droplets sliding down glass).\n"
            "3. [SPEECH]: Includi le battute parlate o il dialogo se presenti nell'idea. Metti il testo parlato esattamente tra virgolette doppie, es: [SPEECH] \"Welcome to our story.\"\n"
            "4. [SOUND]: Descrivi dettagliatamente il paesaggio sonoro ambientale e gli effetti acustici (es. [SOUND] distant rumble of thunder, soft footsteps on gravel, ambient forest birds chirping).\n"
            "5. Evita assolutamente parole di buzz generiche o qualità vuote come 'hyperrealistic', '8k', 'best quality', 'cinematic masterpiece'. Usa invece dettagli tangibili di cinematografia vera.\n"
            "RESTITUISCI SOLTANTO IL PROMPT FINALE STRUTTURATO CON I TAG [VISUAL], [SPEECH], [SOUND]."
        )
    elif mode == MODES[1]:
        return base_expert + (
            "REGOLE DI PROMPTING PER LTX 2.3 STANDARD:\n"
            "1. Scrivi un singolo paragrafo fluido e altamente descrittivo di 4-8 frasi, tutto al presente indicativo.\n"
            "2. Concentrati su coerenza temporale, fluidità del movimento dei soggetti e progressione naturale della scena.\n"
            "3. Specifica l'obiettivo fotografico o l'estetica della cinepresa (es. 35mm lens, anamorphic lens flare, shallow depth of field with creamy bokeh).\n"
            "4. Descrivi con chiarezza la direzione della luce, le ombre, la resa delle superfici fisiche e i dettagli espressivi dei soggetti.\n"
            "RESTITUISCI SOLTANTO IL PARAGRAFO DEL PROMPT FINALE IN INGLESE."
        )
    elif mode == MODES[2]:
        return base_expert + (
            "REGOLE DI PROMPTING PER LTX 2.3 MULTIPLE SUBJECT REFERENCE (MSR Ref Distilled 1.1 22B su Wan2GP):\n"
            "1. Questa modalità lavora abbinata a 2-5 immagini di riferimento fornite (sfondo per primo, poi soggetti o character sheets su sfondo bianco).\n"
            "2. Il tuo prompt deve descrivere chiaramente come i soggetti di riferimento interagiscono all'interno dello sfondo specificato.\n"
            "3. Identifica con coerenza i tratti salienti dei soggetti di riferimento per garantire l'esatta identità visiva lungo tutto il video.\n"
            "4. Descrivi l'azione fluida e i movimenti di camera cinematografici in un paragrafo descrittivo nitido e coordinato.\n"
            "RESTITUISCI SOLTANTO IL PROMPT IN INGLESE."
        )
    elif mode == MODES[3]:
        return base_expert + (
            "REGOLE DI PROMPTING PER LTX 2.3 EDITANYTHING REF V2V (Instruction-Style Editing su Wan2GP):\n"
            "1. Questo modello NON accetta descrizioni narrative passive della scena, ma richiede ISTRUZIONI IMPERATIVE E DIRETTE su cosa modificare rispetto alla reference video/image.\n"
            "2. Inizia le frasi con verbi di comando chiari come: Add, Remove, Replace, Change, Turn, Rotate, Recolor, Relight.\n"
            "3. Specifica cosa deve cambiare e cosa DEVE rimanere inalterato (es. 'Replace the cloudy sky with a vibrant sunset sky, keep the woman, her face, and camera motion unchanged').\n"
            "4. Sii conciso, categorico e preciso.\n"
            "RESTITUISCI SOLTANTO LE ISTRUZIONI DI MODIFICA IN INGLESE."
        )
    elif mode == MODES[4]:
        return base_expert + (
            "REGOLE DI PROMPTING PER JOYAI-ECHO 22B (Storytelling Multi-Finestra su Wan2GP):\n"
            "1. JoyAI-Echo è un modello LTX-2.3 per racconti continui su più scatti (Sliding Windows) con memoria persistente di personaggi, luoghi e oggetti.\n"
            "2. Struttura il prompt in blocchi sequenzialmente separati per ogni finestra/scena, utilizzando i comandi inline ufficiali di Wan2GP in parentesi quadre all'inizio della riga:\n"
            "   - [/duration=5s] o [/duration=120]: definisce la durata del segmento.\n"
            "   - [/overlap=9]: imposta i fotogrammi di transizione e continuità con il segmento precedente.\n"
            "   - [/new_shot]: forza uno stacco netto senza sovrapposizione (hard cut) per cambiare scena o inquadratura.\n"
            "   - [/store_mem=protagonist,room] / [/load_mem=protagonist]: salva o carica memorie di soggetti tra le finestre.\n"
            "3. Esempio di struttura:\n"
            "[/duration=5s,/store_mem=hero] A medium shot of a detective entering a dark office, flashlight beams cutting through dusty air.\n"
            "[/duration=4s,/overlap=9,/load_mem=hero] The detective walks toward a mahogany desk, picking up a mysterious glowing relic.\n"
            "[/new_shot,/duration=4s] A sharp cut to the rainy street outside the office building at night.\n"
            "RESTITUISCI SOLTANTO LA SEQUENZA DEL PROMPT FORMATTATA CON I COMANDI IN INGLESE."
        )
    elif mode == MODES[5]:
        return base_expert + (
            "REGOLE DI PROMPTING PER WAN 2.1 / 2.2 IMAGE-TO-VIDEO (I2V):\n"
            "1. Poiché l'immagine di partenza fornisce già l'aspetto fisico, i colori, i vestiti e la composizione di base, NON RIDESCRIVERE i dettagli fermi già presenti nell'immagine!\n"
            "2. Il tuo prompt deve concentrarsi ESCLUSIVAMENTE sull'evoluzione temporale, sulla dinamica del movimento fisico e sul movimento di camera.\n"
            "3. Esempio perfetto: 'the woman smiles warmly, turns her head toward the rain outside the window, and the camera slowly pushes in with a subtle pan left.'\n"
            "4. Scrivi un prompt conciso, mirato al movimento vitale e alla coerenza cinetica.\n"
            "RESTITUISCI SOLTANTO IL PROMPT IN INGLESE."
        )
    elif mode == MODES[6]:
        return base_expert + (
            "REGOLE DI PROMPTING PER WAN 2.1 / 2.2 TEXT-TO-VIDEO (T2V):\n"
            "1. Scrivi una descrizione cinematografica completa e fotorealistica dell'intera scena da zero.\n"
            "2. Specifica il soggetto, l'abbigliamento, l'ambiente, l'illuminazione tridimensionale, la tavolozza dei colori e l'atmosfera emotiva.\n"
            "3. Includi una descrizione esplicita del movimento della telecamera (es. smooth tracking shot, low angle looking up, crane shot descending).\n"
            "4. Evita termini banali e genera un paragrafo ricco e altamente evocativo di 5-8 frasi in inglese.\n"
            "RESTITUISCI SOLTANTO IL PROMPT IN INGLESE."
        )
    elif mode == MODES[7]:
        return base_expert + (
            "REGOLE DI PROMPTING PER SCAIL 2 CHARACTER ANIMATOR / DANCING (Sliding Windows su Wan2GP):\n"
            "1. Scail 2 è progettato per animare personaggi (fino a 5) in sequenze lunghe o balli ininterrotti grazie alla logica a finestre scorrevoli.\n"
            "2. Scrivi ogni linea del prompt in modo che corrisponda a un movimento o passo di danza successivo nella coreografia temporale.\n"
            "3. Inizia ogni linea con i modificatori di finestra appropriati se necessario (es. [/duration=4s,/overlap=9]).\n"
            "4. Specifica la dinamica corporea energetica, il ritmo visivo e la coerenza del soggetto in movimento in inglese.\n"
            "RESTITUISCI SOLTANTO LE RIGHE DEL PROMPT COREOGRAFICO."
        )
    return base_expert


def format_user_prompt(mode: str, user_idea: str, has_image: bool = False, extra_instructions: str = "") -> str:
    """Prepara il messaggio utente da inviare all'LLM combinando l'idea grezza e le istruzioni aggiuntive."""
    prompt = f"IDEA O DESCRIZIONE GREZZA DELL'UTENTE:\n\"\"\"{user_idea}\"\"\"\n\n"
    if has_image:
        prompt += "NOTA: È stata allegata anche una o più IMMAGINI DI RIFERIMENTO. Analizza attentamente l'estetica, i soggetti, i colori e la composizione delle immagini per integrare e rispettare fedelmente questi elementi nel prompt generato.\n\n"
    if extra_instructions:
        prompt += f"ISTRUZIONI AGGIUNTIVE DELL'UTENTE:\n{extra_instructions}\n\n"
    prompt += "Genera ora il prompt perfetto in inglese seguendo rigorosamente le regole del System Prompt sopra specificate."
    return prompt


def clean_generated_prompt(mode: str, raw_text: str) -> str:
    """Pulisce il testo grezzo restituito dall'LLM rimuovendo preamboli o markdown superflui."""
    lines = raw_text.strip().split("\n")
    cleaned_lines = []
    skip_prefixes = [
        "here is", "here's", "sure", "certainly", "delve", "as an ai", "prompt:", "final prompt:", 
        "output:", "generated prompt:", "il prompt perfetto:", "ecco il prompt:"
    ]
    for line in lines:
        stripped_lower = line.strip().lower()
        if any(stripped_lower.startswith(prefix) for prefix in skip_prefixes) and len(line.split()) < 12:
            continue
        if stripped_lower.startswith("```") and len(line.strip()) <= 10:
            continue
        cleaned_lines.append(line)
    result = "\n".join(cleaned_lines).strip()
    return result

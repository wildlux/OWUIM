"""
Traduzioni IT/EN per Open WebUI Manager GUI.
Ogni chiave ha una versione italiana e inglese.
"""

TRANSLATIONS = {
    "it": {
        # MAIN WINDOW
        "window_title": "Open WebUI Manager",
        "ready": "Pronto",

        # STARTUP
        "startup_title": "Avvio Open WebUI + Ollama",
        "startup_status": "Inizializzazione...",
        "skip_button": "Salta e apri la GUI",
        "continue_anyway": "Continua comunque",
        "startup_warning": "Attenzione",

        # TAB NAMES
        "tab_dashboard": "🏠 Dashboard",
        "tab_logs": "📜 Log",
        "tab_models": "🤖 Modelli",
        "tab_archive": "📁 Archivio",
        "tab_voice": "🔊 Voce",
        "tab_mcp": "🔌 MCP",
        "tab_config": "⚙️ Configurazione",
        "tab_info": "ℹ️ Informazioni",

        # DASHBOARD
        "dashboard_title": "Dashboard",
        "service_status": "Stato Servizi",
        "system_resources": "Risorse Sistema",
        "quick_actions": "Azioni Rapide",
        "details_links": "Dettagli e links locali del tuo Computer",
        "start_button": "▶  Avvia",
        "stop_button": "⏹  Ferma",
        "restart_button": "🔄  Riavvia",
        "open_browser": "🌐  Apri Browser",
        "gpu_detecting": "GPU: rilevamento...",
        "gpu_not_detected": "GPU: Non rilevata (solo CPU)",
        "tier_minimal": "MINIMAL - Risorse critiche!",
        "tier_low": "LOW - Timeout ridotti",
        "tier_medium": "MEDIUM - OK",
        "tier_high": "HIGH - Potente",
        "protection_critical": "⚠️ RAM critica",
        "protection_high": "⚡ RAM alta",
        "protection_ok": "✓ OK",
        "close_apps": "Chiudi app non necessarie",
        "system_working": "Sistema funzionante",
        "system_ready_gpu": "Il tuo sistema e' pronto per l'AI con GPU",
        "system_ready": "Il tuo sistema e' pronto per l'AI",
        "archive_desc": "📁 <b>Archivio:</b> Gestisci file locali da usare come Knowledge Base in Open WebUI",
        "voice_desc": "🔊 <b>Voce:</b> Sintesi vocale italiana offline con Piper TTS",
        "mobile_note": "📱 <i>Puoi usare Open WebUI anche da iPhone e Android!</i>",
        "config_menu_link": "👉 Clicca per mostrare il menu'",
        "verifying": "Verifica...",
        "active": "Attivo",
        "inactive": "Non attivo",

        # LOGS
        "logs_title": "Log dei Servizi",
        "refresh_logs": "🔄 Aggiorna Log",
        "clear_logs": "🗑️ Pulisci",
        "follow_logs": "📜 Segui Log",
        "no_logs": "Nessun log disponibile",

        # MODELS
        "installed_models": "Modelli Installati",
        "recommended_models": "Modelli Consigliati",
        "manual_actions": "Azioni Manuali",
        "download_placeholder": "Scrivi nome modello...",
        "download_button": "⬇️ Scarica",
        "remove_placeholder": "Seleziona modello da rimuovere...",
        "remove_button": "🗑️ Rimuovi",
        "confirm_remove": "Conferma",
        "confirm_remove_msg": "Vuoi davvero rimuovere il modello '{model}'?",
        "download_tooltip": "Clicca per scaricare {model}",
        "refresh_models": "🔄 Aggiorna Lista",
        "copy_name": "Copia nome",
        "remove_model": "Rimuovi modello",
        "confirm_remove_title": "Conferma Rimozione",
        "confirm_remove_detail": "Vuoi rimuovere il modello '{model}'?",
        "remove_action": "Rimuovi",
        "confirm_remove_full_title": "Conferma Rimozione Modello",
        "confirm_remove_full_detail": "Il modello verra' eliminato dal disco.\nPotrai riscaricarlo in qualsiasi momento dal tab Modelli.",
        "model_size": "Dimensione: {size}",
        "removing_model": "Rimozione {model}...",
        "enter_model_name": "Inserisci il nome di un modello",
        "downloading_model": "Download {model}...",
        "models_note": "<i>💡 Clicca sul nome del modello per scaricarlo · Legenda: 📅Quotidiano 💻Coding 👁️Vision 🔢Math 💌Sentiment ✍️Scrittura 🌍Traduzioni</i>",
        "models_links": "<i>🌐 Per modelli più aggiornati: <a href='https://ollama.com/library'>ollama.com</a> · <a href='https://huggingface.co/models'>huggingface.co</a> · <a href='https://kaggle.com/models'>kaggle.com</a></i>",

        # CONFIGURATION
        "config_title": "Configurazione",
        "lan_access": "Accesso LAN (Cellulare/Tablet)",
        "enable_lan": "🌐 Abilita LAN",
        "disable_lan": "🔒 Solo Localhost",
        "refresh_ip": "🔄 Aggiorna IP",
        "enable_lan_tooltip": "Permette l'accesso da altri dispositivi sulla rete",
        "disable_lan_tooltip": "Limita l'accesso solo a questo computer",
        "refresh_ip_tooltip": "Aggiorna indirizzo IP",
        "https_section": "HTTPS (per Microfono)",
        "https_info": "Necessario per usare il microfono da dispositivi mobili.",
        "configure_https": "🔐 Configura HTTPS",
        "configure_https_tooltip": "Genera certificato SSL per connessioni sicure",
        "italian_language": "Lingua Italiana",
        "italian_guide": "🇮🇹 Guida Configurazione Italiano",
        "italian_guide_tooltip": "Mostra come impostare Open WebUI in italiano",
        "maintenance": "Manutenzione",
        "update_button": "⬆️ Aggiorna OpenWebUI",
        "update_tooltip": "Scarica l'ultima versione di Open WebUI",
        "repair_button": "🔧 Ripara",
        "repair_tooltip": "Riavvia i container e pulisce la cache",
        "backup_button": "💾 Backup USB",
        "backup_tooltip": "Crea backup dei dati su USB",
        "update_ollama_button": "🦙 Aggiorna Ollama",
        "update_ollama_tooltip": "Apri il sito ufficiale per aggiornare Ollama",
        "update_docker_button": "🐳 Aggiorna Docker",
        "update_docker_tooltip": "Apri il sito ufficiale per aggiornare Docker",
        "lan_disabled_title": "Accesso LAN Disabilitato",
        "lan_disabled_msg": "🔒 Accesso limitato a localhost.\n\nSolo questo PC puo' accedere a Open WebUI.",
        "lan_enabled_title": "✅ Accesso LAN Abilitato",
        "https_script_error": "Script HTTPS non trovato",
        "italian_guide_title": "Guida Configurazione Italiano",
        "lan_instructions": (
            "<div style='background-color: #e8f4fc; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>📱 Come collegarsi dal cellulare:</b><br><br>"
            "<b>1.</b> Connetti il cellulare alla <b>stessa rete WiFi</b> del PC<br><br>"
            "<b>2.</b> Clicca il pulsante verde <b>\"🌐 Abilita LAN\"</b><br><br>"
            "<b>3.</b> Scansiona il <b>QR code</b> oppure digita l'indirizzo mostrato<br><br>"
            "<hr style='border: 1px solid #bdd7ea;'>"
            "<small>💡 Per tornare alla modalità sicura, clicca <b>\"🔒 Solo Localhost\"</b></small>"
            "</div>"
        ),
        "refresh_ip_btn": "🔄 Aggiorna IP",
        "backup_usb_button": "💾 Backup in USB",
        "https_info_text": "Necessario per usare il microfono da dispositivi mobili.",
        "scan_qr_title": "📱 Scansiona il QR Code dal cellulare",
        "log_copied": "Log copiato negli appunti!",
        "copy_logs_label": "📋 Copia per Supporto",

        # TTS WIDGET
        "tts_status": "Stato Servizio",
        "tts_verifying": "Verifica in corso...",
        "tts_on": "TTS ON",
        "tts_off": "TTS OFF",
        "start_service": "Avvia Servizio",
        "refresh": "Aggiorna",
        "available_voices": "<b>Voci Italiane Disponibili</b>",
        "download_voice": "Scarica",
        "download_all": "📥 Scarica Tutte",
        "voice_test": "Test Voce",
        "voice_selector": "Voce:",
        "test_text_placeholder": "Testo...",
        "test_button": "🔊 Test",
        "play_button": "▶ Riproduci",
        "result_placeholder": "Risultato...",
        "tts_ready": "PRONTO - {count} voci installate",
        "tts_missing": "VOCI MANCANTI - Scarica sotto!",
        "tts_piper_missing": "PIPER MANCANTE",
        "tts_partial": "Parziale - {count} voci",
        "tts_offline": "Non attivo - Avvia il servizio",
        "tts_stopped": "Servizio TTS fermato - memoria liberata",
        "tts_starting": "Avvio in corso...",
        "voice_installed": "Installata",
        "voice_not_installed": "Non installata - Clicca Scarica",
        "voice_ok": "✓ OK",
        "tts_config_title": "Come configurare Open WebUI",
        "tts_config_go_to": "<b>Vai a:</b> Open WebUI → Impostazioni → Audio → Sintesi Vocale (TTS)",
        "tts_param_engine": "Motore",
        "tts_param_url": "URL API",
        "tts_param_key": "Chiave",
        "tts_param_voice": "Voce",
        "tts_docker_title": "<b style='color: #e67e22;'>Per Docker:</b>",
        "voice_label": "Voce:",
        "voice_downloading": "Download voce {voice} in corso...\nQuesto potrebbe richiedere qualche minuto.",
        "voice_installed_msg": "Voce {voice} installata con successo!",
        "tts_error_stop": "Errore stop: {error}",
        "tts_engine": "Engine",
        "tts_api_url": "API URL",
        "tts_api_key": "Chiave",
        "tts_voice": "Voce",
        "copy_config": "📋 Copia",
        "apply_config": "⚙️ Applica",
        "config_copied": "Copiato",
        "config_copied_msg": "Configurazione copiata!",
        "tts_synthesizing": "Sintesi in corso con voce '{voice}'...",
        "tts_insert_text": "Inserisci un testo da sintetizzare!",
        "tts_not_configured": "Sintesi Vocale Non Configurata",
        "tts_install_prompt": "La sintesi vocale di Open WebUI non funzionera' finche' non installi le voci.\n\nVoci mancanti: {missing}\n\nVuoi andare al tab 'Voce' per installarle ora?",
        "download_voices_title": "Scarica Voci",
        "download_voices_confirm": "Vuoi scaricare Piper TTS e tutte le voci italiane?\n\nVerranno scaricati:\n• Piper TTS (~15 MB)\n• Voce Paola (~30 MB)\n• Voce Riccardo (~30 MB)\n\nTotale: ~75 MB",
        "voices_downloading": "Download avviato...\nControlla la finestra del terminale.",

        # ARCHIVE
        "archive_browse": "Esplora File",
        "back_tooltip": "Indietro",
        "up_tooltip": "Cartella superiore",
        "home_tooltip": "Vai alla cartella preferita",
        "refresh_tooltip": "Aggiorna",
        "path_placeholder": "Nessuna cartella selezionata",
        "favorite_tooltip": "Imposta come cartella preferita",
        "browse_tooltip": "Sfoglia cartelle",
        "select_file": "Seleziona un file",
        "base64_button": "📄 Base64",
        "open_button": "📂 Apri",
        "path_button": "📋 Percorso",
        "copy_result": "📋 Copia Risultato",
        "remove_volume": "🗑️ Rimuovi Volume",
        "export_result": "Risultato esportazione:",
        "result_archive_placeholder": "Seleziona un file e clicca Base64...",
        "how_it_works": "💡 Come Funziona?",
        "simple_steps": "📋 3 Passi Semplici",
        "select_private_folder": "Seleziona Cartella Privata",
        "favorite_set": "⭐ Cartella preferita: {path}",
        "select_folder_first": "Seleziona prima una cartella",
        "volume_copied": "Configurazione volume copiata!",
        "copy_volume_tooltip": "Copia configurazione",
        "volume_added_title": "Volume Docker Aggiunto",
        "volume_added_msg": "La cartella e' stata aggiunta al docker-compose.yml come volume:\n\n  {path}:/app/backend/data/uploads/{name}\n\nRiavvia Docker per applicare le modifiche:\n  docker compose down && docker compose up -d",
        "confirm_remove_volume": "Conferma Rimozione",
        "confirm_remove_volume_msg": "Rimuovere il volume Docker per:\n{path}?",
        "volume_removed": "Volume Rimosso",
        "volume_removed_msg": "Volume rimosso dal docker-compose.yml.\nRiavvia Docker per applicare le modifiche.",
        "no_volume_found": "Nessun volume trovato per questa cartella.",
        "file_too_large": "File troppo grande",
        "file_too_large_msg": "Il file e' troppo grande (>10 MB).\nSeleziona un file piu' piccolo.",
        "export_text_button": "📄 Esporta Testo",
        "linked_folders": "Cartelle collegate a Open WebUI:",
        "unlink_button": "🗑️ Scollega",
        "restore_button": "♻️ Ripristina",
        "refresh_volumes_tooltip": "Aggiorna lista volumi",
        "no_linked_folder": "Nessuna cartella collegata",
        "unlink_tooltip": "Scollega la cartella selezionata da Open WebUI",
        "restore_tooltip": "Ricollega una cartella scollegata in precedenza",
        "select_info": "Seleziona prima un file dalla lista",
        "export_first": "Esporta prima un file per copiare il risultato",
        "result_placeholder_archive": "Seleziona un file e clicca Esporta Testo...",
        "confirm_unlink_title": "Conferma Scollegamento",
        "confirm_unlink_msg": "Scollegare la cartella da Open WebUI?\n\n  {name}\n  ({path})\n\nI file NON vengono cancellati dal disco.\nPotrai ripristinarla in qualsiasi momento.",
        "folder_unlinked_title": "Cartella Scollegata",
        "folder_unlinked_msg": "'{name}' scollegata da Open WebUI.\n\nRiavvia Docker per applicare.\nUsa 'Ripristina' per ricollegarla.",
        "no_restore_title": "Nessun Ripristino Disponibile",
        "no_restore_msg": "Non ci sono cartelle scollegate da ripristinare.\n\nUsa ⭐ per collegare una nuova cartella.",
        "restore_folder_title": "Ripristina Cartella",
        "restore_folder_prompt": "Seleziona la cartella da ricollegare a Open WebUI:",
        "folder_not_found_title": "Cartella Non Trovata",
        "folder_not_found_msg": "La cartella non esiste piu':\n{path}\n\nRimuoverla dalla cronologia?",
        "folder_restored_title": "Cartella Ripristinata",
        "folder_restored_msg": "'{name}' ricollegata a Open WebUI.\n\nRiavvia Docker per applicare le modifiche.",
        "folder_already_linked": "La cartella risulta gia' collegata.",
        "archive_purpose": (
            "<div style='background-color: #e8f6e8; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>🎯 A cosa serve?</b><br><br>"
            "Open WebUI ha dei <b>bug</b> quando importi file dal browser.<br><br>"
            "Questa funzione crea un <b>\"cloud privato\"</b> sul tuo PC:<br><br>"
            "✅ I tuoi file <b>restano sul computer</b><br>"
            "✅ Niente upload su internet<br>"
            "✅ Open WebUI li vede senza errori<br>"
            "✅ Bypassa i problemi di importazione</div>"
        ),
        "archive_chat_note": (
            "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px;'>"
            "<b>💬 Per usare i file in chat:</b><br>"
            "<code style='background: #fff; padding: 2px 5px;'>@nome_knowledge descrivi questo</code></div>"
        ),
        "archive_steps_title": "<b style='font-size: 13px;'>📋 3 Passi Semplicissimi</b>",
        "path_copied": "📎 Percorso copiato:\n{path}",
        "copied_to_clipboard": "✓ Copiato negli appunti!",
        "folder_added_archive": "⭐ Cartella aggiunta come archivio documenti: {path}",

        # INFO
        "info_title": "Open WebUI Manager",
        "about_program": "Cosa fa questo programma",
        "thanks": "Ringraziamenti",
        "shortcuts_title": "Scorciatoie Tastiera",
        "support_title": "Supporto",
        "report_issue": "🐛 Segnala un Problema",
        "copy_for_support": "📋 Copia per Supporto",

        # MCP
        "mcp_warning_title": "⚠️ Avviso Importante",
        "mcp_resources": "📊 Risorse Sistema",
        "mcp_service_title": "🔌 MCP Bridge Service (porta 5558)",
        "mcp_start": "🚀 Avvia",
        "mcp_stop": "⏹️ Ferma",
        "mcp_not_started": "Non avviato",
        "mcp_active": "Attivo - {count} tools disponibili",
        "mcp_stopped": "Servizio fermato",
        "mcp_starting": "Avvio in corso...",
        "connected_services": "Servizi Collegati",
        "start_all_services": "Avvia Tutti i Servizi",
        "start_service_btn": "Avvia",
        "mcp_tools_title": "Tools MCP Disponibili",
        "tools_placeholder": "Avvia il servizio per vedere i tools...",
        "lan_access_mcp": "🌐 Accesso LAN",
        "copy_url": "📋 Copia URL",
        "docs_button": "📚 Docs",
        "quick_tests": "🧪 Test Rapidi",
        "test_text": "Testo:",
        "test_text_default": "Ciao, questo e' un test!",
        "test_tts_btn": "🔊 Test TTS",
        "check_services_btn": "🔍 Check Servizi",
        "open_swagger": "📚 Apri Swagger",
        "test_result_placeholder": "I risultati dei test appariranno qui...",
        "detect_resources": "🔄 Rileva",
        "mcp_confirm_title": "⚠️ Conferma Avvio MCP Service",
        "mcp_confirm_question": "<b>Vuoi avviare il servizio MCP Bridge?</b>",
        "mcp_force_start": "⚠️ Avvia comunque (RISCHIOSO)",
        "mcp_start_error": "Errore",
        "mcp_start_error_msg": "Impossibile avviare il servizio:\n{error}",
        "mcp_stop_error_msg": "Impossibile fermare il servizio:\n{error}",
        "mcp_suggestion_title": "Supporto AI Avanzato",
        "mcp_suggestion_text": "<b>Ho notato che il tuo computer supporta nativamente l'AI</b>",
        "mcp_suggestion_info": "Posso abilitare MCP (Model Context Protocol) per offrirti il massimo di prestazioni sulle risposte?\n\nMCP collega i servizi TTS, Analisi Immagini e Documenti per un'esperienza AI completa.",
        "mcp_enable": "Abilita MCP",
        "mcp_not_now": "Non ora",
        "mcp_bridge_started": "MCP Bridge avviato sulla porta 5558",
        "mcp_warning_text": "⚠️ <b style='color: #856404;'>MCP richiede risorse.</b> <span style='color: #856404; font-size: 10px;'>Verifica RAM/VRAM prima di avviare.</span>",
        "mcp_not_active": "MCP non attivo",
        "mcp_already_active": "{service} gia' attivo",
        "mcp_starting_service": "Avvio {service} in corso...",
        "mcp_service_started": "{service} avviato",
        "mcp_service_not_responding": "{service} non risponde - riprova",
        "mcp_service_stopped": "{service} fermato",
        "mcp_error_stopping": "Errore fermando {service}: {error}",
        "mcp_all_active": "Tutti i servizi sono gia' attivi",
        "mcp_starting_n": "Avvio di {count} servizi...",
        "mcp_no_tools": "Nessun tool disponibile",
        "mcp_test_running": "⏳ Test TTS in corso...",
        "mcp_test_checking": "⏳ Verifica servizi in corso...",
        "mcp_service_unreachable": "❌ Servizio MCP non raggiungibile.\n\nCosa fare:\n1. Vai alla sezione 'MCP Bridge Service' qui sopra\n2. Clicca 'Avvia Servizio'\n3. Attendi che lo stato diventi verde\n4. Riprova il test",
        "mcp_start_svc_btn": "Avvia",
        "mcp_stop_svc_btn": "Ferma",
        "mcp_checking_btn": "Verifica...",
        "mcp_starting_btn": "Avvio...",
        "mcp_start_all_tooltip": "Avvia TTS, Image e Document in un colpo solo",
        "mcp_readme_not_found": "README non trovato",
        "mcp_risk_level": "Livello di Rischio: {level}",
        "mcp_system_eval": "Valutazione Sistema:",
        "mcp_what_happens": "Cosa succede avviando il servizio:",
        "mcp_recommendations": "Raccomandazioni:",
        "mcp_tools_placeholder": "Avvia il servizio per vedere i tools...",
        "mcp_test_text_label": "Testo:",
        "mcp_test_input_default": "Ciao, questo è un test!",
        "mcp_test_input_placeholder": "Inserisci testo per il test TTS...",
        "mcp_test_results_placeholder": "I risultati dei test appariranno qui...",
        "copied_clipboard": "Copiato negli appunti:\n{text}",
        "mcp_file_not_found": "File non trovato: {file}",
        "mcp_port_suggestion": "Suggerimenti:\n- Verifica che la porta {port} sia libera\n- Controlla i log per maggiori dettagli",
        "mcp_start_suggestion": "Suggerimenti:\n- Verifica che Python sia installato\n- Controlla che la porta {port} sia libera\n- Prova ad avviare manualmente: python3 mcp_service/mcp_service.py",
        "mcp_stop_manual": "Prova manualmente: pkill -f mcp_service.py",
        "mcp_services_status": "📊 Stato Servizi:\n",
        "mcp_test_tts_ok": "✅ TTS OK!\nVoce: {voice}\nAudio: {size} bytes\nFile: {path}",
        "mcp_no_gpu": "Non rilevata (no GPU NVIDIA o driver)",
        "mcp_ram_error": "Errore: {error}",

        # BOTTOM BAR
        "font_label": "Font:",
        "dark_mode": "🌙 Dark Mode",
        "light_mode": "☀️ Light Mode",

        # COMMON
        "error": "Errore",
        "confirm": "Conferma",
        "warning": "Avviso",
        "info": "Informazione",
        "success": "Successo",
        "copied": "Copiato",
        "copied_msg": "Copiato negli appunti:\n{text}",
        "done": "Fatto",
        "file_not_found": "File non trovato: {path}",
        "script_not_found": "Script non trovato",
        "starting_msg": "Avvio servizi...",
        "stopping_msg": "Arresto servizi...",
        "restarting_msg": "Riavvio servizi...",
        "cancel": "Annulla",
        "close": "Chiudi",
        "retry": "Riprova",
        "view_log": "Vedi Log",

        # DASHBOARD TOOLTIPS
        "start_tooltip": "Avvia Docker e Open WebUI (Ctrl+1)",
        "stop_tooltip": "Ferma tutti i container Docker (Ctrl+S)",
        "restart_tooltip": "Riavvia i servizi Docker",
        "open_browser_tooltip": "Apri Open WebUI nel browser (Ctrl+B)",
        "last_check": "Ultimo controllo:",
        "tts_timeout_label": "Timeout TTS: {tts}s | LLM: {llm}s",
        "gpu_not_detected_label": "GPU: Non rilevata (solo CPU)",

        # FIRST RUN DIALOG
        "first_run_title": "Benvenuto in Open WebUI Manager!",
        "first_run_welcome": "Benvenuto!",
        "first_run_intro": "Per iniziare, segui questi 3 passi:",
        "first_run_step1": "Modelli",
        "first_run_step1_desc": "Scarica almeno un modello AI (consigliato: qwen2.5:7b)",
        "first_run_step2": "Voce",
        "first_run_step2_desc": "Configura la sintesi vocale italiana (opzionale)",
        "first_run_step3": "Browser",
        "first_run_step3_desc": "Apri Open WebUI e inizia a chattare!",
        "first_run_ok_hint": "Premi OK per andare al tab Modelli.",
        "dont_show_again": "Non mostrare piu'",

        # GLOBAL HELP (F1)
        "help_title": "Guida Rapida",
        "help_shortcuts": "Scorciatoie Tastiera",
        "help_nav_tabs": "Naviga tra i tab",
        "help_refresh": "Aggiorna stato servizi",
        "help_open_browser": "Apri browser Open WebUI",
        "help_dark_mode": "Dark/Light mode",
        "help_quit": "Esci",
        "help_this_guide": "Questa guida",
        "help_first_start": "Primo Avvio",
        "help_step1": "Scarica un modello dal tab <b>Modelli</b>",
        "help_step2": "Avvia i servizi dalla <b>Dashboard</b>",
        "help_step3": "Apri il browser per usare Open WebUI",
        "help_useful_links": "Link Utili",

        # TAB HELP
        "tab_help_dashboard": "Panoramica dello stato dei servizi.\n\nDa qui puoi avviare, fermare o riavviare Docker e Open WebUI,\ne monitorare le risorse del sistema.",
        "tab_help_models": "Gestisci i modelli AI di Ollama.\n\nScarica nuovi modelli dalla tabella consigliati\no inserisci manualmente il nome.\nClicca sul nome del modello per scaricarlo.",
        "tab_help_voice": "Sintesi vocale italiana offline con Piper TTS.\n\nConfigura e testa le voci italiane.\nScarica le voci se non ancora installate.",
        "tab_help_archive": "Gestisci file locali da usare come archivio documenti.\n\nTrascina o aggiungi file che verranno indicizzati\nda Open WebUI per le risposte.",
        "tab_help_mcp": "Model Context Protocol Bridge.\n\nEspone i servizi locali (TTS, Image, Document)\ntramite protocollo MCP per integrazioni esterne.",
        "tab_help_config": "Impostazioni avanzate.\n\nAccesso LAN, HTTPS, lingua italiana,\nmanutenzione e backup.",
        "tab_help_logs": "Log dei container Docker in tempo reale.\n\nUtile per diagnosticare problemi.\nUsa 'Segui Log' per lo streaming continuo.",
        "tab_help_info": "Informazioni sul progetto,\nversione e crediti.",
        "tab_help_none": "Nessun aiuto disponibile.",
        "help_guide_prefix": "Guida",

        # CLOSE DIALOG
        "close_title": "Chiudi Open WebUI Manager",
        "close_services_active": "Ci sono servizi ancora attivi.\nCosa vuoi fare?",
        "close_manager": "Chiudi Manager",
        "stop_and_close": "Ferma tutto e chiudi",

        # TRAY
        "tray_show": "Mostra",
        "tray_start": "Avvia Servizi",
        "tray_stop": "Ferma Servizi",
        "tray_browser": "Apri Browser",
        "tray_quit": "Esci",
        "tray_still_running": "L'applicazione e' ancora in esecuzione nel system tray",
        "op_completed": "Operazione completata",
        "op_error": "Errore operazione",
        "op_success": "Successo",

        # ERROR DIALOG
        "error_dialog_title": "Operazione non riuscita",
        "error_dialog_msg": "L'operazione e' terminata con codice errore {code}.\n\nSuggerimenti:",
        "error_docker_check": "Verifica che Docker sia in esecuzione",
        "error_docker_restart": "Prova a riavviare Docker Desktop",
        "error_disk_space": "Controlla lo spazio disco disponibile",
        "error_ollama_check": "Verifica che Ollama sia in esecuzione",
        "error_internet": "Controlla la connessione internet",
        "error_model_name": "Il nome del modello potrebbe essere errato",
        "error_already_removed": "Il modello potrebbe essere gia' stato rimosso",
        "error_check_logs": "Controlla i log per maggiori dettagli",
        "error_check_services": "Verifica che tutti i servizi siano attivi",
        "cancelled": "Annullato",
        "completed_success": "Completato con successo",
        "op_cancelled_user": "Operazione annullata dall'utente",

        # STARTUP THREAD
        "startup_checking_docker": "Verifica Docker...",
        "startup_starting_docker": "Avvio Docker Desktop...",
        "startup_docker_unavailable": "Docker Desktop non disponibile.\nAvvialo manualmente e riprova.",
        "startup_docker_unavailable_linux": "Docker non disponibile.\nInstalla Docker e riprova.",
        "startup_docker_ok": "Docker OK",
        "startup_checking_ollama": "Verifica Ollama...",
        "startup_starting_ollama": "Avvio Ollama...",
        "startup_ollama_unavailable": "Ollama non disponibile.\nInstalla Ollama e riprova.",
        "startup_ollama_ok": "Ollama OK",
        "startup_starting_webui": "Avvio Open WebUI...",
        "startup_downloading_image": "Download immagine...",
        "startup_containers_failed": "Impossibile avviare i container.\n\nVerifica che Docker sia in esecuzione.",
        "startup_container_started": "Container avviato",
        "startup_waiting_service": "Attesa servizio...",
        "startup_ready": "Pronto!",
        "startup_all_started": "Tutti i servizi avviati!",
        "startup_waiting_docker": "Attesa Docker Desktop... ({i}/40)",
        "startup_waiting_ollama_msg": "Attesa Ollama... ({i}/20)",
        "startup_waiting_service_msg": "Attesa servizio... ({i}/30)",

        # INFO WIDGET CONTENT
        "info_desc_html": (
            "Questo programma gestisce un sistema di intelligenza artificiale locale "
            "basato su <b>Open WebUI</b> e <b>Ollama</b>.<br><br>"
            "Permette di:<br>"
            "• Avviare e fermare i servizi AI con un click<br>"
            "• Scaricare e gestire modelli di linguaggio (LLM)<br>"
            "• Convertire immagini per la compatibilita' con la chat<br>"
            "• Usare la sintesi vocale italiana offline<br>"
            "• Accedere all'interfaccia web da cellulare e tablet<br><br>"
            "Tutto funziona <b>localmente</b> sul tuo computer, senza inviare dati a server esterni.<br><br>"
            "🛡️ <b>Protezione anti-Rootkit</b> a livello di rete LAN: il software e' blindato dall'interno."
        ),
        "info_thanks_html": (
            "<div style='text-align: center;'>"
            "<p style='font-size: 12px; color: #2c3e50;'>"
            "Grazie a questo software <b>open source</b>, scaricabile su "
            "<a href='https://github.com/wildlux/OWUIM' style='color: #333;'>GitHub</a>, "
            "puoi sfruttare il tuo computer per lavorare <b>offline</b> "
            "e mantenere un profilo professionale senza dipendere da internet.<br>"
            "Tutti i dati restano sul tuo dispositivo: <b>privacy totale</b>, nessuna informazione condivisa con terzi.<br>"
            "Sviluppato da <b>Paolo Lo Bello</b> | Versione <b>1.1.0</b> | Licenza Open Source<br>"
            "<a href='https://wildlux.pythonanywhere.com/' style='color: #27ae60;'>Sito</a> · "
            "<a href='https://paololobello.altervista.org/' style='color: #e74c3c;'>Blog</a> · "
            "<a href='https://www.linkedin.com/in/paololobello/' style='color: #0077b5;'>LinkedIn</a>"
            "</p>"
            "</div>"
        ),
        "info_shortcuts_html": (
            "<table style='font-size: 11px;'>"
            "<tr><td><b>Ctrl+1..8</b></td><td style='padding-left:12px;'>Passa al tab corrispondente</td></tr>"
            "<tr><td><b>Ctrl+R</b></td><td style='padding-left:12px;'>Aggiorna stato servizi</td></tr>"
            "<tr><td><b>Ctrl+B</b></td><td style='padding-left:12px;'>Apri Open WebUI nel browser</td></tr>"
            "<tr><td><b>Ctrl+F</b></td><td style='padding-left:12px;'>Cambia font (Arial / OpenDyslexic / DejaVu)</td></tr>"
            "</table>"
        ),
        "report_issue_tooltip": "Apri GitHub Issues per segnalare un bug o proporre un miglioramento",
        "support_desc": "Descrivi il problema e includi eventuali messaggi di errore",

        # MAIN WINDOW EXTRA
        "executing": "Esecuzione...",
        "font_saved": "Font {scale}% salvato come predefinito",
        "font_changed": "Font cambiato: {font}",

        # CONFIG WIDGET EXTRA
        "lan_mobile_info": (
            "📱 Per collegarti dal cellulare:\n\n"
            "   Indirizzo:  http://{ip}:{port}\n\n"
            "   1. Connetti il cellulare alla stessa WiFi\n"
            "   2. Apri il browser e vai all'indirizzo sopra\n"
            "   3. Effettua il login con le tue credenziali"
        ),
        "no_qr_install": "(Installa 'qrcode' per vedere il QR:\npip install qrcode[pil])",
        "pwa_instructions": (
            "<b>📲 Installa come App (PWA):</b><br><br>"
            "1. Apri Chrome sul cellulare<br>"
            "2. Scansiona il QR code o vai all'indirizzo<br>"
            "3. Menu ⋮ → 'Aggiungi a schermata Home'<br>"
            "4. Avrai un'icona come app!<br><br>"
            "<i>⚠️ Cellulare e PC devono essere sulla stessa WiFi</i>"
        ),
        "enabling_lan": "Abilitazione accesso LAN...",
        "disabling_lan": "Disabilitazione accesso LAN...",
        "configuring_https": "Configurazione HTTPS...",
        "checking": "Controllo...",
        "italian_guide_html": (
            "<h2>Configurazione Italiano in Open WebUI</h2>"
            "<h3>1. Lingua Interfaccia</h3>"
            "<p>Settings → Interface → Language → <b>Italiano</b></p>"
            "<h3>2. System Prompt</h3>"
            "<p>Settings → Personalization → System Prompt</p>"
            "<pre style='background: #f5f5f5; padding: 10px;'>"
            "Sei un assistente AI che risponde SEMPRE in italiano.\n"
            "Non importa la lingua della domanda, rispondi sempre in italiano.\n"
            "Usa un linguaggio chiaro, professionale e amichevole.</pre>"
            "<h3>3. Modello Predefinito</h3>"
            "<p>Settings → Models → Default Model → <b>mistral:7b-instruct</b> (consigliato)</p>"
        ),
        "version_check_error_title": "Errore Controllo Versione",
        "version_check_error_msg": "Impossibile verificare la versione:\n{error}\n\nVerifica la connessione internet.",
        "update_title": "Aggiornamento Open WebUI",
        "update_up_to_date": "Open WebUI e' gia' aggiornato!",
        "update_version_installed": "Versione installata: <b>{current}</b>",
        "update_version_latest": "Ultima disponibile: <b>{latest}</b> ({date})",
        "update_no_action": "Nessun aggiornamento necessario.",
        "update_changelog": "Novita'",
        "update_available": "Nuova versione disponibile!",
        "update_details": (
            "L'aggiornamento scarichera' la nuova immagine Docker\n"
            "e riavviera' i servizi. I tuoi dati saranno preservati."
        ),
        "update_now": "Aggiorna Ora",
        "update_not_now": "Non Ora",
        "updating_openwebui": "Aggiornamento Open WebUI...",
        "repairing_openwebui": "Riparazione Open WebUI...",
        "backup_title": "Backup",
        "backup_windows_msg": (
            "Su Windows, usa il File Explorer per copiare manualmente:\n\n"
            "• Cartella: {path}\n"
            "• Volumi Docker (open-webui-data)"
        ),

        # TTS WIDGET EXTRA
        "tts_ready_detail": "TTS pronto.\nVoci: {voices}",
        "tts_no_voices_warning": (
            "⚠️ ATTENZIONE: La sintesi vocale NON funzionera'!\n\n"
            "Devi scaricare almeno una voce italiana.\n"
            "Usa i pulsanti 'Scarica' qui sotto."
        ),
        "tts_piper_not_installed": "Piper TTS non installato.\nClicca 'Scarica Tutte' per installare.",
        "tts_error_generic": "Errore: {error}",
        "tts_error_http": "Errore HTTP: {code}",
        "tts_test_success": (
            "✓ Test completato!\n"
            "Voce: {voice}\n"
            "Dimensione: {size} KB\n"
            "Tempo: {time} ms\n"
            "Offline: {offline}"
        ),
        "tts_test_error": "✗ Errore: {error}",
        "tts_test_ensure_active": "Assicurati che il servizio TTS sia attivo.",
        "tts_audio_playing": "▶ Audio in riproduzione...",
        "tts_audio_downloading": "⏳ Download audio...",
        "tts_audio_system_player": "▶ Audio aperto nel player di sistema",
        "tts_playback_complete": "✓ Riproduzione completata",
        "tts_player_error": "✗ Errore player: {error}",
        "tts_audio_download_error": "✗ Errore download audio: {code}",
        "tts_playback_error": "✗ Errore riproduzione: {error}",
        "tts_player_open_error": "✗ Errore apertura player: {error}",
        "tts_unknown_error": "Errore sconosciuto",
        "tts_docker_not_found": "File di configurazione Docker (docker-compose.yml) non trovato",
        "tts_apply_confirm": "Vuoi modificare docker-compose.yml per usare le voci italiane locali?\n\nVerra' creato un backup del file originale.",
        "tts_apply_success": "docker-compose.yml aggiornato!\n\nRiavvia Open WebUI con:\ndocker compose down && docker compose up -d",
        "yes_offline": "SI",
        "no_offline": "NO",

        # ARCHIVIO EXTRA
        "archive_step1_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #27ae60; margin: 2px 0;'>"
            "<b style='color: #27ae60;'>1.</b> <b>Scegli la cartella</b><br>"
            "Naviga e clicca ⭐ sulla cartella desiderata</div>"
        ),
        "archive_step2_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #f39c12; margin: 2px 0;'>"
            "<b style='color: #f39c12;'>2.</b> <b>Copia nel file di configurazione</b></div>"
        ),
        "archive_step3_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #3498db; margin: 2px 0;'>"
            "<b style='color: #3498db;'>3.</b> <b>Riavvia Docker</b><br>"
            "Fatto! I file ⭐ saranno visibili in Open WebUI</div>"
        ),
        "archive_volume_placeholder": "- /percorso/cartella:/app/backend/data/uploads",
        "archive_folder_missing_tooltip": "Cartella non trovata sul disco",
        "archive_exported": "✓ Esportato: {filename}",
        "archive_type": "Tipo: {mime}",
        "archive_base64_length": "Lunghezza Base64: {length} caratteri",
        "archive_compatible_chat": "Compatibile chat: {compat}",
        "archive_compatible_yes": "SI",
        "archive_compatible_no": "NO (troppo grande per chat)",
        "archive_export_error": "✗ Errore: {error}",

        # LOGS EXTRA
        "loading_realtime_logs": "Caricamento log in tempo reale...",
        "no_log_entries": "(nessun log)",
        "log_error": "Errore: {error}",
    },

    "en": {
        # MAIN WINDOW
        "window_title": "Open WebUI Manager",
        "ready": "Ready",

        # STARTUP
        "startup_title": "Starting Open WebUI + Ollama",
        "startup_status": "Initializing...",
        "skip_button": "Skip and open GUI",
        "continue_anyway": "Continue anyway",
        "startup_warning": "Warning",

        # TAB NAMES
        "tab_dashboard": "🏠 Dashboard",
        "tab_logs": "📜 Logs",
        "tab_models": "🤖 Models",
        "tab_archive": "📁 Archive",
        "tab_voice": "🔊 Voice",
        "tab_mcp": "🔌 MCP",
        "tab_config": "⚙️ Configuration",
        "tab_info": "ℹ️ Information",

        # DASHBOARD
        "dashboard_title": "Dashboard",
        "service_status": "Service Status",
        "system_resources": "System Resources",
        "quick_actions": "Quick Actions",
        "details_links": "Details and local computer links",
        "start_button": "▶  Start",
        "stop_button": "⏹  Stop",
        "restart_button": "🔄  Restart",
        "open_browser": "🌐  Open Browser",
        "gpu_detecting": "GPU: detecting...",
        "gpu_not_detected": "GPU: Not detected (CPU only)",
        "tier_minimal": "MINIMAL - Critical resources!",
        "tier_low": "LOW - Reduced timeouts",
        "tier_medium": "MEDIUM - OK",
        "tier_high": "HIGH - Powerful",
        "protection_critical": "⚠️ RAM critical",
        "protection_high": "⚡ RAM high",
        "protection_ok": "✓ OK",
        "close_apps": "Close unnecessary apps",
        "system_working": "System working",
        "system_ready_gpu": "Your system is ready for AI with GPU",
        "system_ready": "Your system is ready for AI",
        "archive_desc": "📁 <b>Archive:</b> Manage local files as Knowledge Base in Open WebUI",
        "voice_desc": "🔊 <b>Voice:</b> Italian offline speech synthesis with Piper TTS",
        "mobile_note": "📱 <i>You can also use Open WebUI from iPhone and Android!</i>",
        "config_menu_link": "👉 Click to show menu",
        "verifying": "Checking...",
        "active": "Active",
        "inactive": "Inactive",

        # LOGS
        "logs_title": "Service Logs",
        "refresh_logs": "🔄 Refresh Logs",
        "clear_logs": "🗑️ Clear",
        "follow_logs": "📜 Follow Logs",
        "no_logs": "No logs available",

        # MODELS
        "installed_models": "Installed Models",
        "recommended_models": "Recommended Models",
        "manual_actions": "Manual Actions",
        "download_placeholder": "Type model name...",
        "download_button": "⬇️ Download",
        "remove_placeholder": "Select model to remove...",
        "remove_button": "🗑️ Remove",
        "confirm_remove": "Confirm",
        "confirm_remove_msg": "Do you really want to remove the model '{model}'?",
        "download_tooltip": "Click to download {model}",
        "refresh_models": "🔄 Refresh List",
        "copy_name": "Copy name",
        "remove_model": "Remove model",
        "confirm_remove_title": "Confirm Removal",
        "confirm_remove_detail": "Do you want to remove the model '{model}'?",
        "remove_action": "Remove",
        "confirm_remove_full_title": "Confirm Model Removal",
        "confirm_remove_full_detail": "The model will be deleted from disk.\nYou can re-download it anytime from the Models tab.",
        "model_size": "Size: {size}",
        "removing_model": "Removing {model}...",
        "enter_model_name": "Enter a model name",
        "downloading_model": "Downloading {model}...",
        "models_note": "<i>💡 Click model name to download · Legend: 📅Daily 💻Coding 👁️Vision 🔢Math 💌Sentiment ✍️Writing 🌍Translation</i>",
        "models_links": "<i>🌐 For more models: <a href='https://ollama.com/library'>ollama.com</a> · <a href='https://huggingface.co/models'>huggingface.co</a> · <a href='https://kaggle.com/models'>kaggle.com</a></i>",

        # CONFIGURATION
        "config_title": "Configuration",
        "lan_access": "LAN Access (Mobile/Tablet)",
        "enable_lan": "🌐 Enable LAN",
        "disable_lan": "🔒 Localhost Only",
        "refresh_ip": "🔄 Refresh IP",
        "enable_lan_tooltip": "Allow access from other devices on the network",
        "disable_lan_tooltip": "Restrict access to this computer only",
        "refresh_ip_tooltip": "Update IP address",
        "https_section": "HTTPS (for Microphone)",
        "https_info": "Required to use microphone on mobile devices.",
        "configure_https": "🔐 Configure HTTPS",
        "configure_https_tooltip": "Generate SSL certificate for secure connections",
        "italian_language": "Italian Language",
        "italian_guide": "🇮🇹 Italian Configuration Guide",
        "italian_guide_tooltip": "Show how to set Open WebUI to Italian",
        "maintenance": "Maintenance",
        "update_button": "⬆️ Update OpenWebUI",
        "update_tooltip": "Download the latest version of Open WebUI",
        "repair_button": "🔧 Repair",
        "repair_tooltip": "Restart containers and clean cache",
        "backup_button": "💾 USB Backup",
        "backup_tooltip": "Backup data to USB",
        "update_ollama_button": "🦙 Update Ollama",
        "update_ollama_tooltip": "Open official site to update Ollama",
        "update_docker_button": "🐳 Update Docker",
        "update_docker_tooltip": "Open official site to update Docker",
        "lan_disabled_title": "LAN Access Disabled",
        "lan_disabled_msg": "🔒 Access limited to localhost.\n\nOnly this PC can access Open WebUI.",
        "lan_enabled_title": "✅ LAN Access Enabled",
        "https_script_error": "HTTPS script not found",
        "italian_guide_title": "Italian Configuration Guide",
        "lan_instructions": (
            "<div style='background-color: #e8f4fc; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>📱 How to connect from mobile:</b><br><br>"
            "<b>1.</b> Connect your phone to the <b>same WiFi network</b> as the PC<br><br>"
            "<b>2.</b> Click the green button <b>\"🌐 Enable LAN\"</b><br><br>"
            "<b>3.</b> Scan the <b>QR code</b> or type the displayed address<br><br>"
            "<hr style='border: 1px solid #bdd7ea;'>"
            "<small>💡 To return to safe mode, click <b>\"🔒 Localhost Only\"</b></small>"
            "</div>"
        ),
        "refresh_ip_btn": "🔄 Refresh IP",
        "backup_usb_button": "💾 USB Backup",
        "https_info_text": "Required to use microphone on mobile devices.",
        "scan_qr_title": "📱 Scan QR Code from your phone",
        "log_copied": "Log copied to clipboard!",
        "copy_logs_label": "📋 Copy for Support",

        # TTS WIDGET
        "tts_status": "Service Status",
        "tts_verifying": "Checking...",
        "tts_on": "TTS ON",
        "tts_off": "TTS OFF",
        "start_service": "Start Service",
        "refresh": "Refresh",
        "available_voices": "<b>Available Italian Voices</b>",
        "download_voice": "Download",
        "download_all": "📥 Download All",
        "voice_test": "Voice Test",
        "voice_selector": "Voice:",
        "test_text_placeholder": "Text...",
        "test_button": "🔊 Test",
        "play_button": "▶ Play",
        "result_placeholder": "Result...",
        "tts_ready": "READY - {count} voices installed",
        "tts_missing": "MISSING VOICES - Download below!",
        "tts_piper_missing": "PIPER MISSING",
        "tts_partial": "Partial - {count} voices",
        "tts_offline": "Inactive - Start the service",
        "tts_stopped": "TTS service stopped - memory freed",
        "tts_starting": "Starting...",
        "voice_installed": "Installed",
        "voice_not_installed": "Not installed - Click Download",
        "voice_ok": "✓ OK",
        "tts_config_title": "How to configure Open WebUI",
        "tts_config_go_to": "<b>Go to:</b> Open WebUI → Settings → Audio → Speech Synthesis (TTS)",
        "tts_param_engine": "Engine",
        "tts_param_url": "API URL",
        "tts_param_key": "Key",
        "tts_param_voice": "Voice",
        "tts_docker_title": "<b style='color: #e67e22;'>For Docker:</b>",
        "voice_label": "Voice:",
        "voice_downloading": "Downloading voice {voice}...\nThis may take a few minutes.",
        "voice_installed_msg": "Voice {voice} installed successfully!",
        "tts_error_stop": "Stop error: {error}",
        "tts_engine": "Engine",
        "tts_api_url": "API URL",
        "tts_api_key": "Key",
        "tts_voice": "Voice",
        "copy_config": "📋 Copy",
        "apply_config": "⚙️ Apply",
        "config_copied": "Copied",
        "config_copied_msg": "Configuration copied!",
        "tts_synthesizing": "Synthesizing with voice '{voice}'...",
        "tts_insert_text": "Enter text to synthesize!",
        "tts_not_configured": "Speech Synthesis Not Configured",
        "tts_install_prompt": "Open WebUI speech synthesis won't work until you install voices.\n\nMissing voices: {missing}\n\nWould you like to go to the 'Voice' tab to install them now?",
        "download_voices_title": "Download Voices",
        "download_voices_confirm": "Do you want to download Piper TTS and all Italian voices?\n\nWill be downloaded:\n• Piper TTS (~15 MB)\n• Paola voice (~30 MB)\n• Riccardo voice (~30 MB)\n\nTotal: ~75 MB",
        "voices_downloading": "Download started...\nCheck the terminal window.",

        # ARCHIVE
        "archive_browse": "File Explorer",
        "back_tooltip": "Back",
        "up_tooltip": "Parent folder",
        "home_tooltip": "Go to favorite folder",
        "refresh_tooltip": "Refresh",
        "path_placeholder": "No folder selected",
        "favorite_tooltip": "Set as favorite folder",
        "browse_tooltip": "Browse folders",
        "select_file": "Select a file",
        "base64_button": "📄 Base64",
        "open_button": "📂 Open",
        "path_button": "📋 Path",
        "copy_result": "📋 Copy Result",
        "remove_volume": "🗑️ Remove Volume",
        "export_result": "Export result:",
        "result_archive_placeholder": "Select a file and click Base64...",
        "how_it_works": "💡 How It Works?",
        "simple_steps": "📋 3 Simple Steps",
        "select_private_folder": "Select Private Folder",
        "favorite_set": "⭐ Favorite folder: {path}",
        "select_folder_first": "Select a folder first",
        "volume_copied": "Volume configuration copied!",
        "copy_volume_tooltip": "Copy configuration",
        "volume_added_title": "Docker Volume Added",
        "volume_added_msg": "Folder added to docker-compose.yml as volume:\n\n  {path}:/app/backend/data/uploads/{name}\n\nRestart Docker to apply changes:\n  docker compose down && docker compose up -d",
        "confirm_remove_volume": "Confirm Removal",
        "confirm_remove_volume_msg": "Remove Docker volume for:\n{path}?",
        "volume_removed": "Volume Removed",
        "volume_removed_msg": "Volume removed from docker-compose.yml.\nRestart Docker to apply changes.",
        "no_volume_found": "No volume found for this folder.",
        "file_too_large": "File too large",
        "file_too_large_msg": "File is too large (>10 MB).\nSelect a smaller file.",
        "export_text_button": "📄 Export Text",
        "linked_folders": "Folders linked to Open WebUI:",
        "unlink_button": "🗑️ Unlink",
        "restore_button": "♻️ Restore",
        "refresh_volumes_tooltip": "Refresh volumes list",
        "no_linked_folder": "No linked folders",
        "unlink_tooltip": "Unlink the selected folder from Open WebUI",
        "restore_tooltip": "Re-link a previously unlinked folder",
        "select_info": "Select a file from the list first",
        "export_first": "Export a file first to copy the result",
        "result_placeholder_archive": "Select a file and click Export Text...",
        "confirm_unlink_title": "Confirm Unlink",
        "confirm_unlink_msg": "Unlink folder from Open WebUI?\n\n  {name}\n  ({path})\n\nFiles will NOT be deleted from disk.\nYou can restore it anytime.",
        "folder_unlinked_title": "Folder Unlinked",
        "folder_unlinked_msg": "'{name}' unlinked from Open WebUI.\n\nRestart Docker to apply.\nUse 'Restore' to re-link.",
        "no_restore_title": "No Restore Available",
        "no_restore_msg": "No unlinked folders to restore.\n\nUse ⭐ to link a new folder.",
        "restore_folder_title": "Restore Folder",
        "restore_folder_prompt": "Select folder to re-link to Open WebUI:",
        "folder_not_found_title": "Folder Not Found",
        "folder_not_found_msg": "Folder no longer exists:\n{path}\n\nRemove from history?",
        "folder_restored_title": "Folder Restored",
        "folder_restored_msg": "'{name}' re-linked to Open WebUI.\n\nRestart Docker to apply changes.",
        "folder_already_linked": "Folder is already linked.",
        "archive_purpose": (
            "<div style='background-color: #e8f6e8; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>🎯 What is this for?</b><br><br>"
            "Open WebUI has <b>bugs</b> when importing files from the browser.<br><br>"
            "This feature creates a <b>\"private cloud\"</b> on your PC:<br><br>"
            "✅ Your files <b>stay on your computer</b><br>"
            "✅ No upload to internet<br>"
            "✅ Open WebUI sees them without errors<br>"
            "✅ Bypasses import issues</div>"
        ),
        "archive_chat_note": (
            "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px;'>"
            "<b>💬 To use files in chat:</b><br>"
            "<code style='background: #fff; padding: 2px 5px;'>@knowledge_name describe this</code></div>"
        ),
        "archive_steps_title": "<b style='font-size: 13px;'>📋 3 Simple Steps</b>",
        "path_copied": "📎 Path copied:\n{path}",
        "copied_to_clipboard": "✓ Copied to clipboard!",
        "folder_added_archive": "⭐ Folder added as document archive: {path}",

        # INFO
        "info_title": "Open WebUI Manager",
        "about_program": "What this program does",
        "thanks": "Acknowledgments",
        "shortcuts_title": "Keyboard Shortcuts",
        "support_title": "Support",
        "report_issue": "🐛 Report a Problem",
        "copy_for_support": "📋 Copy for Support",

        # MCP
        "mcp_warning_title": "⚠️ Important Warning",
        "mcp_resources": "📊 System Resources",
        "mcp_service_title": "🔌 MCP Bridge Service (port 5558)",
        "mcp_start": "🚀 Start",
        "mcp_stop": "⏹️ Stop",
        "mcp_not_started": "Not started",
        "mcp_active": "Active - {count} tools available",
        "mcp_stopped": "Service stopped",
        "mcp_starting": "Starting...",
        "connected_services": "Connected Services",
        "start_all_services": "Start All Services",
        "start_service_btn": "Start",
        "mcp_tools_title": "Available MCP Tools",
        "tools_placeholder": "Start the service to see tools...",
        "lan_access_mcp": "🌐 LAN Access",
        "copy_url": "📋 Copy URL",
        "docs_button": "📚 Docs",
        "quick_tests": "🧪 Quick Tests",
        "test_text": "Text:",
        "test_text_default": "Hello, this is a test!",
        "test_tts_btn": "🔊 Test TTS",
        "check_services_btn": "🔍 Check Services",
        "open_swagger": "📚 Open Swagger",
        "test_result_placeholder": "Test results will appear here...",
        "detect_resources": "🔄 Detect",
        "mcp_confirm_title": "⚠️ Confirm MCP Service Startup",
        "mcp_confirm_question": "<b>Do you want to start the MCP Bridge service?</b>",
        "mcp_force_start": "⚠️ Start anyway (RISKY)",
        "mcp_start_error": "Error",
        "mcp_start_error_msg": "Cannot start the service:\n{error}",
        "mcp_stop_error_msg": "Cannot stop the service:\n{error}",
        "mcp_suggestion_title": "Advanced AI Support",
        "mcp_suggestion_text": "<b>I noticed your computer natively supports AI</b>",
        "mcp_suggestion_info": "Can I enable MCP (Model Context Protocol) to provide maximum performance on responses?\n\nMCP connects TTS, Image Analysis and Documents services for a complete AI experience.",
        "mcp_enable": "Enable MCP",
        "mcp_not_now": "Not now",
        "mcp_bridge_started": "MCP Bridge started on port 5558",
        "mcp_warning_text": "⚠️ <b style='color: #856404;'>MCP requires resources.</b> <span style='color: #856404; font-size: 10px;'>Check RAM/VRAM before starting.</span>",
        "mcp_not_active": "MCP not active",
        "mcp_already_active": "{service} already active",
        "mcp_starting_service": "Starting {service}...",
        "mcp_service_started": "{service} started",
        "mcp_service_not_responding": "{service} not responding - retry",
        "mcp_service_stopped": "{service} stopped",
        "mcp_error_stopping": "Error stopping {service}: {error}",
        "mcp_all_active": "All services are already active",
        "mcp_starting_n": "Starting {count} services...",
        "mcp_no_tools": "No tools available",
        "mcp_test_running": "⏳ TTS test in progress...",
        "mcp_test_checking": "⏳ Checking services...",
        "mcp_service_unreachable": "❌ MCP service unreachable.\n\nWhat to do:\n1. Go to 'MCP Bridge Service' section above\n2. Click 'Start Service'\n3. Wait for green status\n4. Retry the test",
        "mcp_start_svc_btn": "Start",
        "mcp_stop_svc_btn": "Stop",
        "mcp_checking_btn": "Checking...",
        "mcp_starting_btn": "Starting...",
        "mcp_start_all_tooltip": "Start TTS, Image and Document all at once",
        "mcp_readme_not_found": "README not found",
        "mcp_risk_level": "Risk Level: {level}",
        "mcp_system_eval": "System Evaluation:",
        "mcp_what_happens": "What happens when starting the service:",
        "mcp_recommendations": "Recommendations:",
        "mcp_tools_placeholder": "Start the service to see available tools...",
        "mcp_test_text_label": "Text:",
        "mcp_test_input_default": "Hello, this is a test!",
        "mcp_test_input_placeholder": "Enter text for TTS test...",
        "mcp_test_results_placeholder": "Test results will appear here...",
        "copied_clipboard": "Copied to clipboard:\n{text}",
        "mcp_file_not_found": "File not found: {file}",
        "mcp_port_suggestion": "Suggestions:\n- Check that port {port} is free\n- Check the logs for more details",
        "mcp_start_suggestion": "Suggestions:\n- Verify that Python is installed\n- Check that port {port} is free\n- Try starting manually: python3 mcp_service/mcp_service.py",
        "mcp_stop_manual": "Try manually: pkill -f mcp_service.py",
        "mcp_services_status": "📊 Services Status:\n",
        "mcp_test_tts_ok": "✅ TTS OK!\nVoice: {voice}\nAudio: {size} bytes\nFile: {path}",
        "mcp_no_gpu": "Not detected (no NVIDIA GPU or drivers)",
        "mcp_ram_error": "Error: {error}",

        # BOTTOM BAR
        "font_label": "Font:",
        "dark_mode": "🌙 Dark Mode",
        "light_mode": "☀️ Light Mode",

        # COMMON
        "error": "Error",
        "confirm": "Confirm",
        "warning": "Warning",
        "info": "Information",
        "success": "Success",
        "copied": "Copied",
        "copied_msg": "Copied to clipboard:\n{text}",
        "done": "Done",
        "file_not_found": "File not found: {path}",
        "script_not_found": "Script not found",
        "starting_msg": "Starting services...",
        "stopping_msg": "Stopping services...",
        "restarting_msg": "Restarting services...",
        "cancel": "Cancel",
        "close": "Close",
        "retry": "Retry",
        "view_log": "View Log",

        # DASHBOARD TOOLTIPS
        "start_tooltip": "Start Docker and Open WebUI (Ctrl+1)",
        "stop_tooltip": "Stop all Docker containers (Ctrl+S)",
        "restart_tooltip": "Restart Docker services",
        "open_browser_tooltip": "Open Open WebUI in browser (Ctrl+B)",
        "last_check": "Last check:",
        "tts_timeout_label": "Timeout TTS: {tts}s | LLM: {llm}s",
        "gpu_not_detected_label": "GPU: Not detected (CPU only)",

        # FIRST RUN DIALOG
        "first_run_title": "Welcome to Open WebUI Manager!",
        "first_run_welcome": "Welcome!",
        "first_run_intro": "To get started, follow these 3 steps:",
        "first_run_step1": "Models",
        "first_run_step1_desc": "Download at least one AI model (recommended: qwen2.5:7b)",
        "first_run_step2": "Voice",
        "first_run_step2_desc": "Configure Italian speech synthesis (optional)",
        "first_run_step3": "Browser",
        "first_run_step3_desc": "Open Open WebUI and start chatting!",
        "first_run_ok_hint": "Press OK to go to the Models tab.",
        "dont_show_again": "Don't show again",

        # GLOBAL HELP (F1)
        "help_title": "Quick Guide",
        "help_shortcuts": "Keyboard Shortcuts",
        "help_nav_tabs": "Navigate between tabs",
        "help_refresh": "Refresh service status",
        "help_open_browser": "Open Open WebUI browser",
        "help_dark_mode": "Dark/Light mode",
        "help_quit": "Quit",
        "help_this_guide": "This guide",
        "help_first_start": "First Start",
        "help_step1": "Download a model from the <b>Models</b> tab",
        "help_step2": "Start services from the <b>Dashboard</b>",
        "help_step3": "Open the browser to use Open WebUI",
        "help_useful_links": "Useful Links",

        # TAB HELP
        "tab_help_dashboard": "Service status overview.\n\nFrom here you can start, stop or restart Docker and Open WebUI,\nand monitor system resources.",
        "tab_help_models": "Manage Ollama AI models.\n\nDownload new models from the recommended table\nor manually enter the name.\nClick on the model name to download it.",
        "tab_help_voice": "Italian offline speech synthesis with Piper TTS.\n\nConfigure and test Italian voices.\nDownload voices if not yet installed.",
        "tab_help_archive": "Manage local files as document archive.\n\nDrag or add files that will be indexed\nby Open WebUI for responses.",
        "tab_help_mcp": "Model Context Protocol Bridge.\n\nExposes local services (TTS, Image, Document)\nvia MCP protocol for external integrations.",
        "tab_help_config": "Advanced settings.\n\nLAN access, HTTPS, Italian language,\nmaintenance and backup.",
        "tab_help_logs": "Real-time Docker container logs.\n\nUseful for diagnosing problems.\nUse 'Follow Logs' for continuous streaming.",
        "tab_help_info": "Project information,\nversion and credits.",
        "tab_help_none": "No help available.",
        "help_guide_prefix": "Guide",

        # CLOSE DIALOG
        "close_title": "Close Open WebUI Manager",
        "close_services_active": "There are still active services.\nWhat would you like to do?",
        "close_manager": "Close Manager",
        "stop_and_close": "Stop all and close",

        # TRAY
        "tray_show": "Show",
        "tray_start": "Start Services",
        "tray_stop": "Stop Services",
        "tray_browser": "Open Browser",
        "tray_quit": "Quit",
        "tray_still_running": "The application is still running in the system tray",
        "op_completed": "Operation completed",
        "op_error": "Operation error",
        "op_success": "Success",

        # ERROR DIALOG
        "error_dialog_title": "Operation failed",
        "error_dialog_msg": "The operation finished with error code {code}.\n\nSuggestions:",
        "error_docker_check": "Verify that Docker is running",
        "error_docker_restart": "Try restarting Docker Desktop",
        "error_disk_space": "Check available disk space",
        "error_ollama_check": "Verify that Ollama is running",
        "error_internet": "Check your internet connection",
        "error_model_name": "The model name might be incorrect",
        "error_already_removed": "The model might already have been removed",
        "error_check_logs": "Check the logs for more details",
        "error_check_services": "Verify that all services are active",
        "cancelled": "Cancelled",
        "completed_success": "Completed successfully",
        "op_cancelled_user": "Operation cancelled by user",

        # STARTUP THREAD
        "startup_checking_docker": "Checking Docker...",
        "startup_starting_docker": "Starting Docker Desktop...",
        "startup_docker_unavailable": "Docker Desktop not available.\nStart it manually and try again.",
        "startup_docker_unavailable_linux": "Docker not available.\nInstall Docker and try again.",
        "startup_docker_ok": "Docker OK",
        "startup_checking_ollama": "Checking Ollama...",
        "startup_starting_ollama": "Starting Ollama...",
        "startup_ollama_unavailable": "Ollama not available.\nInstall Ollama and try again.",
        "startup_ollama_ok": "Ollama OK",
        "startup_starting_webui": "Starting Open WebUI...",
        "startup_downloading_image": "Downloading image...",
        "startup_containers_failed": "Unable to start containers.\n\nVerify that Docker is running.",
        "startup_container_started": "Container started",
        "startup_waiting_service": "Waiting for service...",
        "startup_ready": "Ready!",
        "startup_all_started": "All services started!",
        "startup_waiting_docker": "Waiting for Docker Desktop... ({i}/40)",
        "startup_waiting_ollama_msg": "Waiting for Ollama... ({i}/20)",
        "startup_waiting_service_msg": "Waiting for service... ({i}/30)",

        # INFO WIDGET CONTENT
        "info_desc_html": (
            "This program manages a local artificial intelligence system "
            "based on <b>Open WebUI</b> and <b>Ollama</b>.<br><br>"
            "It allows you to:<br>"
            "• Start and stop AI services with one click<br>"
            "• Download and manage language models (LLM)<br>"
            "• Convert images for chat compatibility<br>"
            "• Use Italian offline speech synthesis<br>"
            "• Access the web interface from phone and tablet<br><br>"
            "Everything runs <b>locally</b> on your computer, without sending data to external servers.<br><br>"
            "🛡️ <b>Anti-Rootkit protection</b> at LAN network level: the software is hardened from within."
        ),
        "info_thanks_html": (
            "<div style='text-align: center;'>"
            "<p style='font-size: 12px; color: #2c3e50;'>"
            "Thanks to this <b>open source</b> software, downloadable on "
            "<a href='https://github.com/wildlux/OWUIM' style='color: #333;'>GitHub</a>, "
            "you can leverage your computer to work <b>offline</b> "
            "and maintain a professional profile without depending on the internet.<br>"
            "All data stays on your device: <b>total privacy</b>, no information shared with third parties.<br>"
            "Developed by <b>Paolo Lo Bello</b> | Version <b>1.1.0</b> | Open Source License<br>"
            "<a href='https://wildlux.pythonanywhere.com/' style='color: #27ae60;'>Website</a> · "
            "<a href='https://paololobello.altervista.org/' style='color: #e74c3c;'>Blog</a> · "
            "<a href='https://www.linkedin.com/in/paololobello/' style='color: #0077b5;'>LinkedIn</a>"
            "</p>"
            "</div>"
        ),
        "info_shortcuts_html": (
            "<table style='font-size: 11px;'>"
            "<tr><td><b>Ctrl+1..8</b></td><td style='padding-left:12px;'>Switch to corresponding tab</td></tr>"
            "<tr><td><b>Ctrl+R</b></td><td style='padding-left:12px;'>Refresh service status</td></tr>"
            "<tr><td><b>Ctrl+B</b></td><td style='padding-left:12px;'>Open Open WebUI in browser</td></tr>"
            "<tr><td><b>Ctrl+F</b></td><td style='padding-left:12px;'>Change font (Arial / OpenDyslexic / DejaVu)</td></tr>"
            "</table>"
        ),
        "report_issue_tooltip": "Open GitHub Issues to report a bug or suggest an improvement",
        "support_desc": "Describe the problem and include any error messages",

        # MAIN WINDOW EXTRA
        "executing": "Executing...",
        "font_saved": "Font {scale}% saved as default",
        "font_changed": "Font changed: {font}",

        # CONFIG WIDGET EXTRA
        "lan_mobile_info": (
            "📱 To connect from mobile:\n\n"
            "   Address:  http://{ip}:{port}\n\n"
            "   1. Connect your phone to the same WiFi\n"
            "   2. Open the browser and go to the address above\n"
            "   3. Log in with your credentials"
        ),
        "no_qr_install": "(Install 'qrcode' to see the QR:\npip install qrcode[pil])",
        "pwa_instructions": (
            "<b>📲 Install as App (PWA):</b><br><br>"
            "1. Open Chrome on your phone<br>"
            "2. Scan the QR code or go to the address<br>"
            "3. Menu ⋮ → 'Add to Home Screen'<br>"
            "4. You'll have an icon like an app!<br><br>"
            "<i>⚠️ Phone and PC must be on the same WiFi</i>"
        ),
        "enabling_lan": "Enabling LAN access...",
        "disabling_lan": "Disabling LAN access...",
        "configuring_https": "Configuring HTTPS...",
        "checking": "Checking...",
        "italian_guide_html": (
            "<h2>Italian Configuration in Open WebUI</h2>"
            "<h3>1. Interface Language</h3>"
            "<p>Settings → Interface → Language → <b>Italiano</b></p>"
            "<h3>2. System Prompt</h3>"
            "<p>Settings → Personalization → System Prompt</p>"
            "<pre style='background: #f5f5f5; padding: 10px;'>"
            "You are an AI assistant that ALWAYS responds in Italian.\n"
            "No matter the language of the question, always respond in Italian.\n"
            "Use clear, professional and friendly language.</pre>"
            "<h3>3. Default Model</h3>"
            "<p>Settings → Models → Default Model → <b>mistral:7b-instruct</b> (recommended)</p>"
        ),
        "version_check_error_title": "Version Check Error",
        "version_check_error_msg": "Unable to check version:\n{error}\n\nCheck your internet connection.",
        "update_title": "Open WebUI Update",
        "update_up_to_date": "Open WebUI is already up to date!",
        "update_version_installed": "Installed version: <b>{current}</b>",
        "update_version_latest": "Latest available: <b>{latest}</b> ({date})",
        "update_no_action": "No update required.",
        "update_changelog": "What's New",
        "update_available": "New version available!",
        "update_details": (
            "The update will download the new Docker image\n"
            "and restart services. Your data will be preserved."
        ),
        "update_now": "Update Now",
        "update_not_now": "Not Now",
        "updating_openwebui": "Updating Open WebUI...",
        "repairing_openwebui": "Repairing Open WebUI...",
        "backup_title": "Backup",
        "backup_windows_msg": (
            "On Windows, use File Explorer to manually copy:\n\n"
            "• Folder: {path}\n"
            "• Docker volumes (open-webui-data)"
        ),

        # TTS WIDGET EXTRA
        "tts_ready_detail": "TTS ready.\nVoices: {voices}",
        "tts_no_voices_warning": (
            "⚠️ WARNING: Speech synthesis will NOT work!\n\n"
            "You need to download at least one Italian voice.\n"
            "Use the 'Download' buttons below."
        ),
        "tts_piper_not_installed": "Piper TTS not installed.\nClick 'Download All' to install.",
        "tts_error_generic": "Error: {error}",
        "tts_error_http": "HTTP Error: {code}",
        "tts_test_success": (
            "✓ Test complete!\n"
            "Voice: {voice}\n"
            "Size: {size} KB\n"
            "Time: {time} ms\n"
            "Offline: {offline}"
        ),
        "tts_test_error": "✗ Error: {error}",
        "tts_test_ensure_active": "Make sure the TTS service is active.",
        "tts_audio_playing": "▶ Audio playing...",
        "tts_audio_downloading": "⏳ Downloading audio...",
        "tts_audio_system_player": "▶ Audio opened in system player",
        "tts_playback_complete": "✓ Playback complete",
        "tts_player_error": "✗ Player error: {error}",
        "tts_audio_download_error": "✗ Audio download error: {code}",
        "tts_playback_error": "✗ Playback error: {error}",
        "tts_player_open_error": "✗ Player open error: {error}",
        "tts_unknown_error": "Unknown error",
        "tts_docker_not_found": "Docker configuration file (docker-compose.yml) not found",
        "tts_apply_confirm": "Do you want to modify docker-compose.yml to use local Italian voices?\n\nA backup of the original file will be created.",
        "tts_apply_success": "docker-compose.yml updated!\n\nRestart Open WebUI with:\ndocker compose down && docker compose up -d",
        "yes_offline": "YES",
        "no_offline": "NO",

        # ARCHIVIO EXTRA
        "archive_step1_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #27ae60; margin: 2px 0;'>"
            "<b style='color: #27ae60;'>1.</b> <b>Choose the folder</b><br>"
            "Navigate and click ⭐ on the desired folder</div>"
        ),
        "archive_step2_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #f39c12; margin: 2px 0;'>"
            "<b style='color: #f39c12;'>2.</b> <b>Copy to configuration file</b></div>"
        ),
        "archive_step3_html": (
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #3498db; margin: 2px 0;'>"
            "<b style='color: #3498db;'>3.</b> <b>Restart Docker</b><br>"
            "Done! The ⭐ files will be visible in Open WebUI</div>"
        ),
        "archive_volume_placeholder": "- /path/to/folder:/app/backend/data/uploads",
        "archive_folder_missing_tooltip": "Folder not found on disk",
        "archive_exported": "✓ Exported: {filename}",
        "archive_type": "Type: {mime}",
        "archive_base64_length": "Base64 length: {length} characters",
        "archive_compatible_chat": "Chat compatible: {compat}",
        "archive_compatible_yes": "YES",
        "archive_compatible_no": "NO (too large for chat)",
        "archive_export_error": "✗ Error: {error}",

        # LOGS EXTRA
        "loading_realtime_logs": "Loading real-time logs...",
        "no_log_entries": "(no logs)",
        "log_error": "Error: {error}",
    }
}


def get_text(key, lang="it", **kwargs):
    """Ritorna il testo tradotto per la chiave data."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["it"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

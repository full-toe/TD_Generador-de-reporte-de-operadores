# Este script fue diseñado por @full_toe con el fin de generar, en TouchDesigner, un reporte de los operadores que se esten seleccionado para darle contexto a cualquier IA.
# En TouchDesigner, arrastra este txt, seleccioná los operadores que querés reportar y ejecutá este script con clic derecho en el text DAT sin seleccionarlo: Run Script.
# Chequee ultima version del proyecto en Github: https://github.com/full-toe/TD_Generador-de-reporte-de-operadores
# Testeado en la version 2025 de TouchDesigner de Windows.
#
# ⚠️ NOTA DE PRIVACIDAD Y SEGURIDAD:
# Este script analiza la configuración y contenido de los operadores seleccionados. 
# Si seleccionás operadores DAT que contengan contraseñas, API Keys, IPs privadas o credenciales en texto plano, estos datos aparecerán en el reporte. Asegúrate de revisar el texto antes de compartirlo en plataformas públicas o IAs.

import os
import threading
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext

pane = ui.panes.current
parent_op = pane.owner if (pane and pane.type == PaneType.NETWORKEDITOR) else me.parent()

selected_ops = parent_op.selectedChildren

if not selected_ops:
    print("WARNING: No seleccionaste ningún nodo. Marcá los nodos en la red antes de correr el script.")
else:
    # Metadatos de fecha/hora y proyecto
    now = datetime.now()
    fecha_hora_str = now.strftime("%Y-%m-%d %H:%M:%S")
    time_file_str = now.strftime("%Y-%m-%d_%H-%M-%S") # Incluye segundos para evitar duplicados

    proj_name = getattr(project, 'name', 'Sin_Nombre')
    proj_clean_name = proj_name.replace('.toe', '')
    proj_folder = getattr(project, 'folder', '')
    proj_path = os.path.join(proj_folder, proj_name) if proj_folder else "No guardado"
    
    # Rendimiento y FPS
    cook_rate = getattr(project, 'cookRate', 60.0) # FPS Target

    # Medición de FPS Reales mediante Perform CHOP
    actual_fps = cook_rate
    try:
        temp_perf = parent_op.create(performCHOP, '_temp_fps_check')
        actual_fps = float(temp_perf['fps'])
        temp_perf.destroy()
    except Exception:
        actual_fps = cook_rate

    # Medición de VRAM / Memoria de GPU
    gpu_info = "N/A"
    try:
        gpu_used = getattr(app, 'gpuMemoryUsed', None)
        gpu_total = getattr(app, 'gpuMemoryTotal', None)
        if gpu_used is not None and gpu_total is not None:
            gpu_info = f"{gpu_used:.0f}MB / {gpu_total:.0f}MB"
        elif gpu_used is not None:
            gpu_info = f"{gpu_used:.0f}MB"
    except Exception:
        pass

    current_dat_path = me.path

    lines = []

    # --- ENCABEZADO MULTILÍNEA COMPACTO (40 CARACTERES) ---
    box_w = 40
    inner_w = box_w - 4

    def add_box_field(label, val_str):
        full_text = f"▪ {label:<8}: {val_str}"
        words = full_text.split(" ")
        current_line = ""
        
        for w in words:
            if len(current_line) + len(w) + (1 if current_line else 0) <= inner_w:
                current_line += (" " if current_line else "") + w
            else:
                lines.append(f"│ {current_line:<{inner_w}} │")
                current_line = f"  {w}"
        if current_line:
            lines.append(f"│ {current_line:<{inner_w}} │")

    lines.append("┌" + "─" * (box_w - 2) + "┐")
    lines.append(f"│{'REPORTE TÉCNICO PARA IA'.center(box_w - 2)}│")
    lines.append("├" + "─" * (box_w - 2) + "┤")
    
    add_box_field("Fecha", now.strftime('%Y-%m-%d'))
    add_box_field("Hora", now.strftime('%H:%M:%S'))
    add_box_field("Proyecto", proj_name)
    add_box_field("Build TD", f"{app.version} ({app.build})")
    add_box_field("FPS Tar.", f"{cook_rate:.1f} FPS")
    add_box_field("FPS Act.", f"{actual_fps:.1f} FPS")
    if gpu_info != "N/A":
        add_box_field("VRAM GPU", gpu_info)
    add_box_field("Frame", f"{absTime.frame} ({absTime.seconds:.1f}s)")
    add_box_field("Realtime", str(getattr(project, 'realtime', True)))
    add_box_field("Red", parent_op.path)
    add_box_field("Total OP", str(len(selected_ops)))
    
    lines.append("└" + "─" * (box_w - 2) + "┘\n")

    # --- AVISO DE SEGURIDAD EN EL REPORTE ---
    lines.append("⚠️ AVISO DE PRIVACIDAD: Si alguno de los nodos seleccionados contiene contraseñas, API Keys o datos sensibles, revisalos antes de compartir este reporte públicamente.\n")
    lines.append("Chequee ultima version del proyecto en Github: https://github.com/full-toe/TD_Generador-de-reporte-de-operadores\n")

    # --- DETALLE DE NODOS ---
    lines.append("► NODOS SELECCIONADOS EN LA RED:\n")

    for o in selected_ops:
        lines.append(f"▶ OPERADOR: {o.name}")
        lines.append(f"  • Tipo/Familia: {o.type} ({o.OPType}) | Familia: {o.family}")
        lines.append(f"  • Ruta Completa: {o.path}")
        
        # Tiempo de Cook individual del nodo
        cook_time_ms = getattr(o, 'cookTime', 0.0)
        lines.append(f"  • Cook Time: {cook_time_ms:.3f} ms")

        # Banderas (Flags)
        flags = []
        if getattr(o, 'bypass', False): flags.append("BYPASS")
        if getattr(o, 'lock', False): flags.append("LOCKED")
        if hasattr(o, 'allowCook') and not o.allowCook: flags.append("COOK DISABLED")
        if getattr(o, 'display', False): flags.append("DISPLAY")
        if getattr(o, 'render', False): flags.append("RENDER")
        lines.append(f"  • Banderas/Estado: {', '.join(flags) if flags else 'Normal'}")

        # Captura de Errores y Warnings activos
        try:
            err_msg = o.errors() if callable(getattr(o, 'errors', None)) else ""
            warn_msg = o.warnings() if callable(getattr(o, 'warnings', None)) else ""
            if err_msg:
                formatted_err = err_msg.strip().replace('\n', '\n      ')
                lines.append(f"  • ❌ ERROR ACTIVO:\n      {formatted_err}")
            if warn_msg:
                formatted_warn = warn_msg.strip().replace('\n', '\n      ')
                lines.append(f"  • ⚠️ WARNING ACTIVO:\n      {formatted_warn}")
        except Exception as e:
            lines.append(f"  • Errores/Warnings: Error al comprobar ({e})")

        # --- DETALLE DE ENTRADAS ---
        try:
            in_connectors = getattr(o, 'inputConnectors', [])
            in_nodes = []
            if o.family == 'COMP':
                in_nodes = [child for child in o.children if child.type.startswith('in')]
                in_nodes.sort(key=lambda x: (x.nodeY, x.nodeX), reverse=True)

            lines.append(f"  • Entradas ({len(in_connectors)} conectores):")
            if in_connectors:
                for idx, conn in enumerate(in_connectors):
                    in_tag = f"In {idx}: {in_nodes[idx].name}" if idx < len(in_nodes) else f"In {idx}"
                    if conn.connections:
                        conns_str = [f"{c.owner.name} ({c.owner.type}, Salida {c.index})" for c in conn.connections]
                        lines.append(f"      - [{in_tag}] -> Conectado a: {', '.join(conns_str)}")
                    else:
                        lines.append(f"      - [{in_tag}] -> Sin conexión")
            else:
                lines.append("      (Sin entradas)")
        except Exception as e:
            lines.append(f"  • Entradas: Error al leer ({e})")

        # --- DETALLE DE SALIDAS ---
        try:
            out_connectors = getattr(o, 'outputConnectors', [])
            out_nodes = []
            if o.family == 'COMP':
                out_nodes = [child for child in o.children if child.type.startswith('out')]
                out_nodes.sort(key=lambda x: (x.nodeY, x.nodeX), reverse=True)

            lines.append(f"  • Salidas ({len(out_connectors)} conectores):")
            if out_connectors:
                for idx, conn in enumerate(out_connectors):
                    out_tag = f"Out {idx}: {out_nodes[idx].name}" if idx < len(out_nodes) else f"Out {idx}"
                    if conn.connections:
                        conns_str = [f"{c.owner.name} ({c.owner.type}, Entrada {c.index})" for c in conn.connections]
                        lines.append(f"      - [{out_tag}] -> Conectado a: {', '.join(conns_str)}")
                    else:
                        lines.append(f"      - [{out_tag}] -> Sin conexión")
            else:
                lines.append("      (Sin salidas)")
        except Exception as e:
            lines.append(f"  • Salidas: Error al leer ({e})")

        # --- PERSONALIZACIONES (CUSTOM PARAMETERS & BINDINGS) ---
        try:
            custom_pars = getattr(o, 'customPars', [])
            if custom_pars:
                lines.append(f"  • Parámetros Personalizados / Custom ({len(custom_pars)}):")
                for p in custom_pars:
                    val_eval = p.eval()
                    val_str = f"'{val_eval}'" if isinstance(val_eval, str) else str(val_eval)
                    
                    details = []
                    if p.expr:
                        details.append(f"Expr: '{p.expr}'")
                    
                    if hasattr(p, 'bindExpr') and p.bindExpr:
                        details.append(f"BindExpr: '{p.bindExpr}'")
                    if p.mode == ParMode.BIND and hasattr(p, 'bindMaster') and p.bindMaster:
                        details.append(f"BindMaster: {p.bindMaster.owner.path}.par.{p.bindMaster.name}")
                    
                    if hasattr(p, 'bindReferences') and p.bindReferences:
                        refs = [f"{ref.owner.name}.par.{ref.name}" for ref in p.bindReferences]
                        details.append(f"Vinculado internamente a -> {', '.join(refs)}")

                    detail_str = f" [{ ' | '.join(details) }]" if details else ""
                    lines.append(f"      - [{p.page.name}] {p.name} ('{p.label}'): {val_str}{detail_str}")
            else:
                lines.append("  • Parámetros Personalizados: Ninguno")
        except Exception as e:
            lines.append(f"  • Parámetros Personalizados: Error ({e})")

        # Si es CHOP
        if getattr(o, 'isCHOP', False) or o.family == 'CHOP':
            try:
                chans_obj = o.chans() if callable(getattr(o, 'chans', None)) else []
                chans_str = [f"{c.name}: {c.eval():.3f}" for c in chans_obj]
                lines.append(f"  • Canales CHOP ({len(chans_str)}): {', '.join(chans_str) if chans_str else 'Sin canales'}")
            except Exception as e:
                lines.append(f"  • Canales CHOP: Error ({e})")

        # Si es DAT
        if getattr(o, 'isDAT', False) or o.family == 'DAT':
            try:
                raw_text = str(o.text) if hasattr(o, 'text') else ""
                if raw_text.strip():
                    dat_lines = raw_text.splitlines()
                    lines.append(f"  • Contenido DAT ({len(dat_lines)} líneas):")
                    max_preview = 30
                    for l in dat_lines[:max_preview]:
                        lines.append(f"      | {l}")
                    if len(dat_lines) > max_preview:
                        rem = len(dat_lines) - max_preview
                        lines.append(f"      | ... [{rem} líneas más no mostradas en la vista previa. INSTRUCCIÓN PARA IA: Si necesitás analizar la lógica completa de este script para resolver el problema, pedile al usuario el contenido completo del operador '{o.name}' ({o.path})]")
                else:
                    lines.append("  • Contenido DAT: (Vacío)")
            except Exception as e:
                lines.append(f"  • Contenido DAT: Error al leer ({e})")

        # Parámetros estándar modificados
        try:
            mod_pars = [p for p in o.pars() if (not p.isDefault or p.expr) and not p.isCustom]
            lines.append(f"  • Parámetros Estándar Modificados ({len(mod_pars)}):")
            
            if mod_pars:
                for p in mod_pars:
                    val_str = f"'{p.eval()}'" if isinstance(p.eval(), str) else str(p.eval())
                    expr_str = f" [Expr: {p.expr}]" if p.expr else ""
                    lines.append(f"      - {p.name}: {val_str}{expr_str}")
            else:
                lines.append("      (Todos los parámetros estándar por defecto)")
        except Exception as e:
            lines.append(f"  • Parámetros Estándar: Error ({e})")
            
        lines.append("\n" + "-" * 50 + "\n")

    report_text = "\n".join(lines).strip() + "\n\n\n"

    # Copia automática inicial al portapapeles
    ui.clipboard = report_text

    # Ventana Pop-Up flotante no bloqueante
    def build_popup_async(text, name_clean, time_str, dat_path):
        try:
            root = tk.Tk()
            root.title(f"Reporte Técnico para IA - {name_clean}")
            root.geometry("900x700")
            root.attributes('-topmost', True)
            root.configure(bg="#1e1e1e")

            txt_box = scrolledtext.ScrolledText(
                root, 
                font=("Consolas", 10), 
                bg="#1e1e1e", 
                fg="#d4d4d4", 
                insertbackground="white",
                relief="flat"
            )
            txt_box.pack(expand=True, fill='both', padx=10, pady=(10, 5))
            txt_box.insert(tk.INSERT, text)

            btn_frame = tk.Frame(root, bg="#1e1e1e")
            btn_frame.pack(fill='x', padx=10, pady=(5, 10))

            def copiar_portapapeles():
                root.clipboard_clear()
                root.clipboard_append(txt_box.get("1.0", tk.END))
                btn_copy.config(text="¡Copiado!", bg="#2e7d32")
                root.after(2000, lambda: btn_copy.config(text="📋 Copiar al Portapapeles", bg="#007acc"))

            def guardar_txt():
                default_filename = f"reporte_{name_clean}_{time_str}.txt"
                filepath = filedialog.asksaveasfilename(
                    parent=root,
                    title="Guardar Reporte Técnico",
                    initialfile=default_filename,
                    defaultextension=".txt",
                    filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")]
                )
                if filepath:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(txt_box.get("1.0", tk.END))
                    btn_save.config(text="¡Guardado!", bg="#2e7d32")
                    root.after(2000, lambda: btn_save.config(text="💾 Guardar .txt", bg="#333333"))

            def nuevo_reporte():
                run(f"op('{dat_path}').run()", delayFrames=1)

            btn_copy = tk.Button(
                btn_frame, 
                text="📋 Copiar al Portapapeles", 
                command=copiar_portapapeles,
                bg="#007acc", fg="white", 
                activebackground="#005999", activeforeground="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat", padx=12, pady=6, cursor="hand2"
            )
            btn_copy.pack(side='left', padx=(0, 8))

            btn_save = tk.Button(
                btn_frame, 
                text="💾 Guardar .txt", 
                command=guardar_txt,
                bg="#333333", fg="white", 
                activebackground="#444444", activeforeground="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat", padx=12, pady=6, cursor="hand2"
            )
            btn_save.pack(side='left', padx=(0, 8))

            btn_new = tk.Button(
                btn_frame, 
                text="🔄 Nuevo Reporte (OPs seleccionados)", 
                command=nuevo_reporte,
                bg="#4a148c", fg="white", 
                activebackground="#6a1b9a", activeforeground="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat", padx=12, pady=6, cursor="hand2"
            )
            btn_new.pack(side='left')

            root.mainloop()
        except Exception as err:
            print(f"Error en Pop-Up: {err}")

    thread = threading.Thread(
        target=build_popup_async, 
        args=(report_text, proj_clean_name, time_file_str, current_dat_path), 
        daemon=True
    )
    thread.start()

def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    """Versión ULTRA ESTABLE: Corta, escala y pone portada"""
    try:
        # COMANDO SIMPLIFICADO Y POTENTE
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            # Escalar video principal a 1080p exacto
            "-filter_complex",
            f"[0:v]scale={RESOLUCION}:force_original_aspect_ratio=decrease,pad={RESOLUCION}:(ow-iw)/2:(oh-ih)/2,setsar=1[video];"
            f"[1:v]scale=w=200:h=-1[logo];"
            f"[video][logo]overlay=10:10[outv]",
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", CODEC_VIDEO,
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-pix_fmt", "yuv420p",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-c:a", CODEC_AUDIO,
            "-b:a", BITRATE_AUDIO,
            "-movflags", "+faststart",
            ruta_salida
        ]

        # Ejecutar y MOSTRAR ERRORES si quieres depurar (cambia DEVNULL por PIPE)
        resultado = subprocess.run(
            comando,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE, # Capturamos errores
            timeout=TIMEOUT_FFMPEG
        )

        # Verificar que el archivo existe y pesa bien
        if os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 500000: # Mínimo 500KB
            log.info(f"✅ Parte {parte} generada correctamente")
            return f"🎬 {titulo}\n💎 PARTE {parte} DE {total}\n🔗 @MallySeries"
        else:
            log.error(f"❌ Archivo vacío o muy pequeño: {ruta_salida}")
            return None

    except subprocess.CalledProcessError as e:
        log.error(f"💥 Error FFmpeg Parte {parte}: {e.stderr.decode()}")
        return None
    except Exception as e:
        log.error(f"❌ Error general Parte {parte}: {str(e)}")
        return None

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)
from config import (
    TELEGRAM_TOKEN,
    TIPO_CONTACTO,
    NOMBRE_EMPRESA,
    NOMBRE,
    APELLIDO,
    TELEFONO,
    EMAIL,
    EMPRESA_VINCULADA,
    CONFIRMAR,
    ESPERANDO_PLANTILLA,
    CONFIRMANDO_PLANTILLA,
    SELECCIONANDO_EMPRESA_PLANTILLA,
)
from handlers.comandos import start, estado, recientes, mensaje_desconocido
from handlers.conversacion import (
    nuevo,
    elegir_tipo,
    buscar_empresa_plantilla,
    callback_seleccionar_empresa_plantilla,
    recibir_plantilla,
    confirmar_plantilla,
    recibir_nombre_empresa,
    recibir_nombre,
    recibir_apellido,
    recibir_telefono,
    recibir_email,
    recibir_empresa_vinculada,
    callback_empresa,
    confirmar,
    cancelar,
)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("nuevo", nuevo)],
        states={
            TIPO_CONTACTO: [CallbackQueryHandler(elegir_tipo, pattern="^tipo_")],
            NOMBRE_EMPRESA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre_empresa)
            ],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            APELLIDO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_apellido)
            ],
            TELEFONO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_telefono)
            ],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_email)],
            EMPRESA_VINCULADA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, recibir_empresa_vinculada
                ),
                CallbackQueryHandler(callback_empresa, pattern="^empresa_"),
            ],
            CONFIRMAR: [CallbackQueryHandler(confirmar, pattern="^confirmar_")],
            SELECCIONANDO_EMPRESA_PLANTILLA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, buscar_empresa_plantilla
                ),
                CallbackQueryHandler(
                    callback_seleccionar_empresa_plantilla, pattern="^emp_pre"
                ),
            ],
            ESPERANDO_PLANTILLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_plantilla)
            ],
            CONFIRMANDO_PLANTILLA: [
                CallbackQueryHandler(confirmar_plantilla, pattern="^plantilla_")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
        allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("recientes", recientes))
    app.add_handler(conv)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_desconocido)
    )
    print("✅ Bot en marcha. Abre Telegram y escribe /start")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

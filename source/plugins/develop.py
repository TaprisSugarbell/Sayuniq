import io
import os
import sys
import traceback

from hydrogram import Client, enums, filters, types

from source import auth_users


async def aexec(code: str, bot: Client, message: types.Message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n")),
    )
    return await locals()["__aexec"](bot, message)


@Client.on_message(filters.command(["eval"]))
async def __eval__(bot: Client, message: types.Message):
    AUTH_USERS = await auth_users()
    if message.from_user not in AUTH_USERS:
        return

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.reply(text="No has dado nada para evaluar!")
        return
    reply_to_id = message.id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, bot, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Hecho"
    final_output = (
        f"**Entrada:** `{cmd}`\n\n**Resultado:**\n\n```{evaluation.strip()}```"
    )

    if len(final_output) > 4096:
        filename = "salida.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        await message.reply_document(
            document=filename,
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id,
        )
        os.remove(filename)
        await message.delete()
    else:
        await message.reply_text(text=final_output, parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command(commands=["json"]))
async def __eval_json__(bot: Client, message: types.Message):
    json = message.reply_to_message or message
    await message.reply(text=f"```{json}```")

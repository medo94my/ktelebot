import os
import logging
import html
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
from replit import db
import traceback
from telegram import (
 KeyboardButton,
 KeyboardButtonPollType,
 Poll,
 ReplyKeyboardMarkup,
 ReplyKeyboardRemove,
 Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
 CallbackContext,
 Application,
 CommandHandler,
 ContextTypes,
 MessageHandler,
 PollAnswerHandler,
 PollHandler,
 filters,
)
# Enable logging
logging.basicConfig(
 format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
 level=logging.INFO)
logger = logging.getLogger(__name__)

poll_list = []
grp_id='-819086032'
bot_id='809712713'

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	grp_id = update.effective_chat.id
	await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def poll(context: ContextTypes.DEFAULT_TYPE,place_work) -> None:
	today = datetime.date.today()
	# dd/mm/YY
	now = today.strftime("%d/%m/%Y")
	"""Sends a predefined poll"""
	questions = ["1PM", "2PM", "3PM", "4PM"]
	message = await context.bot.send_poll(
	 # update.effective_chat.id,
	 grp_id,
	 """Good day everyone🌞! [ """+now+""" ] Kindly choose your today's breaktime, and please retract your vote if there's too many people in a vote.Thank you and have a great day ahead ⭐️ ("""
	 + place_work + """)""",
	 questions,
	 is_anonymous=False,
	 allows_multiple_answers=False)
	# Save some info about the poll the bot_data for later use in receive_poll_answer
	payload = {
	 message.poll.id: {
	  "questions": questions,
	  "message_id": message.message_id,
	  "chat_id": grp_id,
	  "answers": 0,
	 }
	}
	context.bot_data.update(payload)
	


async def two_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
	await poll(context, "WFH")
	await poll(context, "Campus")


async def receive_poll_answer(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Summarize a users poll vote"""
	answer = update.poll_answer
	answered_poll = context.bot_data[answer.poll_id]
	db[f"msg_id_{answered_poll['message_id']}"] = answered_poll['message_id']
	try:
		questions = answered_poll["questions"]
	# this means this poll answer update is from an old poll, we can't do our answering then
	except KeyError:
		return
	selected_options = answer.option_ids
	answer_string = ""
	for question_id in selected_options:
		print(question_id)
		if question_id != selected_options[-1]:
			answer_string += questions[question_id] + " and "
		else:
			answer_string += questions[question_id]
	if (not answer_string):
		await context.bot.send_message(
		 bot_id,
		 f"{update.effective_user.mention_html()} retacted vote!",
		 parse_mode=ParseMode.HTML,
		)
	else:
		await context.bot.send_message(
		 bot_id,
		 f"{update.effective_user.mention_html()} choosed {answer_string}!",
		 parse_mode=ParseMode.HTML,
		)
async def close_poll(context):
	print(db.keys())
	for key in db.keys():
		try:
			await context.bot.stop_poll(grp_id, db[key])
		except telegram.error.BadRequest:
			continue
		finally:
			del db[key]

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=bot_id, text=message, parse_mode=ParseMode.HTML
    )
my_secret = os.environ['tele_API_KEY']



app = ApplicationBuilder().token(my_secret).build()
app.add_handler(CommandHandler("hello", hello))
# app.add_handler(CommandHandler("poll", two_poll))
app.add_handler(PollAnswerHandler(receive_poll_answer))
  # ...and the error handler
app.add_error_handler(error_handler)



j = app.job_queue

j.run_daily(two_poll, datetime.time(4), days=(0, 1, 2, 3, 4, 5, 6))
j.run_daily(close_poll, datetime.time(6), days=(0, 1, 2, 3, 4, 5, 6))

app.run_polling()

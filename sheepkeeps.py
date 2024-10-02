import asyncio
import requests
import io
import json
import os
import requests
import logging
from PIL import Image
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import img2pdf
import shutil

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)

# Bot configuration
bot_token = "your_bot_token_here"
credentials_file = "google_drive_api_Jason_file_name_here"
folder_ids = {
    'Chemistry': '14gMH4GAdarymi8XwfE-qvCrNVF1CGuEP',
    'Physics': '1I8f4vbJFGxTlOnWO5e5WQUNCSE2NkP60',
    'Mathematics': '1-XVnjVhKUWHYfd1D1FUpRw9U9ql0CgSY'
}

# Step constants for conversation
LINK, FOLDER_CHOICE, SUB_FOLDER_NAME, SUMMARY = range(4)
def format_date_from_name(name_str):
    try:
        # Check if the name string contains an underscore and has the correct length
        if '_' in name_str and len(name_str.split('_')[0]) == 8:
            date_part = name_str.split('_')[0]  # Extract '20240923' from '20240923_102759'
            formatted_date = datetime.strptime(date_part, '%Y%m%d').strftime('%d-%m-%Y')
            return formatted_date
        else:
            logging.error(f"Invalid date string format: {name_str}")
            return "Invalid Date"  # Return a default value or handle it as needed
    except ValueError as e:
        logging.error(f"Date parsing error: {e}")
        return "Invalid Date"  # Return a default value or handle it as needed

#Function to convert link to API endpoint for the first type of link
def convert_link_type_1(link):
    try:
        # Extract the API key from the link
        api_key = link.split('/detail/')[-1].split('/record')[0]
        api_url = f"https://air.ifpshare.com/api/pub/files/{api_key}"
        return api_key, api_url
    except IndexError:
        return None, None

# Function to convert link to API endpoint for the second type of link
def convert_link_type_2(link):
    try:
        # Extract the ID from the link
        api_id = link.split('s_id=')[-1]
        api_url = f"https://air.ifpshare.com/api/shares/{api_id}"
        return api_id, api_url
    except IndexError:
        return None, None

# Function to download image and return as BytesIO
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        logging.error(f"Failed to download image from {url} (Status Code: {response.status_code})")
        return None



def format_dateold(date_str): #not using anymore
    try:
        # Check if the date string contains an underscore and has the correct length
        if '_' in date_str and len(date_str.split('_')[0]) == 8:
            date_part = date_str.split('_')[0]  # Extract '20240923' from '20240923_102759'
            formatted_date = datetime.strptime(date_part, '%Y%m%d').strftime('%d-%m-%Y')
            return formatted_date
        else:
            logging.error(f"Invalid date string format: {date_str}")
            return "Invalid Date"  # Return a default value or handle it as needed
    except ValueError as e:
        logging.error(f"Date parsing error: {e}")
        return "Invalid Date"  # Return a default value or handle it as needed
        
        
def format_date(date_str):
	try:
		date_object = datetime.fromtimestamp(int(date_str))
		formatted_date = date_object.strftime('%d-%m-%Y')
		return formatted_date
	except ValueError:
		return "Invalid Date"

# Function to create a folder in Google Drive
def create_drive_folder(folder_name, parent_id):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

# Function to upload file to Google Drive
def upload_to_drive(file_stream, file_name, folder_id):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(file_stream, mimetype='image/jpeg')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Function to format date from '20240923_102759' to '23-09-2024'
def format_dateold(date_str): #not using anymore
    try:
        # Check if the date string contains an underscore and has the correct length
        if '_' in date_str and len(date_str.split('_')[0]) == 8:
            date_part = date_str.split('_')[0]  # Extract '20240923' from '20240923_102759'
            formatted_date = datetime.strptime(date_part, '%Y%m%d').strftime('%d-%m-%Y')
            return formatted_date
        else:
            logging.error(f"Invalid date string format: {date_str}")
            return "Invalid Date"  # Return a default value or handle it as needed
    except ValueError as e:
        logging.error(f"Date parsing error: {e}")
        return "Invalid Date"  # Return a default value or handle it as needed
    




# Path to the JSON file
PDF_METADATA_FILE = "pdf_metadata.json"

# Load the PDF metadata from JSON file
def load_pdf_metadata():
    if os.path.exists(PDF_METADATA_FILE):
        with open(PDF_METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save the PDF metadata to JSON file
def save_pdf_metadata(metadata):
    with open(PDF_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

# Add a new PDF entry to the metadata file
def add_pdf_entry(link_id, message_id):
    metadata = load_pdf_metadata()
    metadata[link_id] = {
        "message_id": message_id,
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_pdf_metadata(metadata)

# Check if PDF is already generated
def is_pdf_generated(link_id):
    metadata = load_pdf_metadata()
    return metadata.get(link_id)

# Function to retrieve the message_id of the PDF for a link
def get_message_id(link_id):
    metadata = load_pdf_metadata()
    return metadata[link_id]["message_id"] if link_id in metadata else None







# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    

    # Load admin list dynamically from the JSON file
        # Admin buttons
    keyboard = [
        [InlineKeyboardButton("Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("Upload", callback_data="tmp")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)  
    await update.message.reply_text(
        f"✨ 𝗛𝗲𝘆, 𝗜’𝗺 𝗦𝗵𝗲𝗲𝗽𝗞𝗲𝗲𝗽𝘀!\n\n"
        "I’ll keep all your notes *warm and cozy* inside my wool! Whenever you need them, just give me a shout — I’m always around!\n"
        "Be cool, stay calm, and let me do the rest.\n\n"
        "💡 Need help? Just type /help and I’ve got you covered!\n\n"
        "────────── ꌩꂦꀎꋪ ꀤꈤꎇꂦ ──────────\n\n"
        f"𝗬𝗼𝘂𝗿 𝗜𝗗: {user_id}\n"
        "𝗠𝗲𝗺𝗯𝗲𝗿𝘀𝗵𝗶𝗽: Admin",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    ) 




























# Function to download image from a URL
def download_image(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return response.content  # Return image content
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Function to format date from string
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except ValueError as e:
        print(f"Error formatting date: {e}")
        return 'Unknown Date'

# Function to count total images
def count_images(image_links):
    """Count the total number of image links."""
    return len(image_links)

# Function to fetch image links from metadata
def get_image_links(metadata):
    """Extract image links from metadata."""
    return [image['url'] for image in metadata.get('images', []) if 'url' in image]

# Command handler for users to upload images
async def handle_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve the link from the user's input
    input_link = context.args[0] if context.args else None
    if not input_link:
        await update.message.reply_text("Please provide a valid PDF link.")
        return

    # Convert the input link to API format (function not provided in the original code)
    api_key, api_endpoint = convert_link_type_1(input_link)
    if not api_endpoint:
        await update.message.reply_text("The link format is invalid.")
        return

    # Create inline buttons with "Download PDF" and "Fetch Images" side by side
    keyboard = [
        [
            InlineKeyboardButton("Download PDF", callback_data='download_pdf'),
            InlineKeyboardButton("Fetch Images", callback_data='fetch_images'),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data='cancel'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    api_response = requests.get(api_endpoint)
    if api_response.status_code != 200:

        return
    image_metadata = api_response.json()  # Get the full JSON response
    formatted_date = format_date_from_name(image_metadata['name'])
    valid_image_urls = get_image_links(image_metadata)


    # Send a message to the user containing the API key and API URL with buttons
    await update.message.reply_text(
        f"───────── ꌗꀎꂵꂵꍏꋪꌩ ─────────\n\n"
        f"[ # ] 𝗢𝗿𝗶𝗴𝗶𝗻𝗮𝗹 𝗟𝗶𝗻𝗸: {input_link}\n"
        f"[ # ] 𝗔𝗣𝗜 𝗞𝗲𝘆: {api_key}\n\n"
        f"[ # ] 𝗡𝗼𝘁𝗲𝘀 𝗖𝗿𝗲𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲: {formatted_date}\n"
        f"[ # ] 𝗣𝗗𝗙 𝗳𝗶𝗹𝗲 𝗰𝗼𝗻𝘁𝗮𝗶𝗻𝘀: {len(valid_image_urls)} Images\n\n"
        f"─── ꌃꀎ꓄ ꀤ ꒒ꂦꃴꍟ ꃅꍟꋪ ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧ ────",
        reply_markup=reply_markup
    )

    # Store the input link and API key for later use
    context.user_data['input_link'] = input_link
    context.user_data['api_key'] = api_key
    context.user_data['api_endpoint'] = api_endpoint

# Callback query handler for downloading PDF
async def handle_download_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    input_link = context.user_data.get('input_link')
    api_key = context.user_data.get('api_key')
    api_endpoint = context.user_data.get('api_endpoint')
    user_id = update.effective_chat.id  # Get the user's chat ID for folder naming

    if not input_link or not api_endpoint:
        await query.message.reply_text("Missing information. Please try again.")
        return

    # Fetch images from the API
    api_response = requests.get(api_endpoint)
    if api_response.status_code != 200:
        await query.message.reply_text("Failed to retrieve images from the API.")
        return

    image_metadata = api_response.json()  # Get the full JSON response

    # Get image links using the new function
    valid_image_urls = get_image_links(image_metadata)

    # Create a directory for the user
    user_folder = f'images_cache_{user_id}'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    valid_images = []

    # Initialize the download status message
    download_status = (
        "───────── ꌗꃅꍟꍟꉣꀘꍟꍟꉣꌗ ─────────\n\n"
        "[ # ] 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗶𝗺𝗮𝗴𝗲𝘀...\n\n"
        "────── ꂵꀤꌗꌗ ꌩꂦꀎ ꀭꀎ꒒ꀤ (╥﹏╥) ──────\n\n"
    )
    
    # Edit the initial message to show the download status
    await context.bot.edit_message_text(text=download_status, chat_id=update.effective_chat.id, message_id=query.message.message_id)
    
    for img_url in valid_image_urls:
        if img_url:
            image_data = download_image(img_url)
    
            if image_data:
                # Save the image to the user-specific directory
                image_name = img_url.split('/')[-1]  # Extract the image name from the URL
                image_path = os.path.join(user_folder, image_name)
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_data)
    
                valid_images.append(image_path)
    
                # Update the download status message
                download_status += f"[ + ] '{image_name}' downloaded successfully.\n"
            else:
                download_status += f"[ - ] Failed to download '{img_url}'.\n"
        else:
            download_status += "[ - ] Invalid URL.\n"
    
        # Edit the message to show the latest status
        await context.bot.edit_message_text(text=download_status, chat_id=update.effective_chat.id, message_id=query.message.message_id)
    
    # Check if there are valid images to convert
    if not valid_images:
        await context.bot.edit_message_text(text="No valid images downloaded for PDF conversion.", chat_id=update.effective_chat.id, message_id=query.message.message_id)
        return
    
    # Merge images into PDF
    download_status += "[ # ] Merging images into a PDF...\n"
    await context.bot.edit_message_text(text=download_status, chat_id=update.effective_chat.id, message_id=query.message.message_id)
    





    # Fetch formatted date from the "name" field in the metadata
    if 'name' in image_metadata:
        formatted_date = format_date_from_name(image_metadata['name'])
        pdf_filename = f"{formatted_date}_sheepkeeps.pdf"
    else:
        pdf_filename = "default_filename_sheepkeeps.pdf"
    
    merged_pdf_path = os.path.join(user_folder, pdf_filename)
    
    # Convert images to PDF
    with open(merged_pdf_path, 'wb') as pdf_file:
        pdf_file.write(img2pdf.convert(valid_images))
    
    # Prepare the thank-you message
    thank_you_message = (
        "───────── ꀸꃅꍏꌩꍏꅏꍏꀸ ─────────\n\n"
        f"[ # ] 𝗣𝗱𝗳 𝗳𝗶𝗹𝗲 𝗶𝘀 𝘂𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴...\n\n"
        f"Thanks for using our service! If you have any more requests feel free to ask :)\n\n"
        f"[ # ] We convert Maxhub board notes link to PDFs\n\n"
    )
    
    await context.bot.edit_message_text(text=thank_you_message, chat_id=update.effective_chat.id, message_id=query.message.message_id)
    

    api_response = requests.get(api_endpoint)
    if api_response.status_code != 200:

        return
    image_metadata = api_response.json()  # Get the full JSON response
    formatted_date = format_date_from_name(image_metadata['name'])
    
    valid_image_urls = get_image_links(image_metadata)
    # Prepare the temp_message to send along with the PDF
    temp_message = ( 
        "───── ꅏꍟ ꈤꍟꃴꍟꋪ ꓄ꍏ꒒ꀘꍟꀸ ( ._. )"" ─────\n\n" 
        f"[ # ] 𝗢𝗿𝗶𝗴𝗶𝗻𝗮𝗹 𝗟𝗶𝗻𝗸: {input_link}\n" 
        f"[ # ] 𝗔𝗽𝗶 𝗞𝗲𝘆: {api_key}\n\n" 
        f"[ # ] 𝗡𝗼𝘁𝗲𝘀 𝗖𝗿𝗲𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲: {formatted_date}\n" 
        f"[ # ] 𝗣𝗗𝗙 𝗖𝗿𝗲𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲: {datetime.now().strftime('%d-%m-%Y')}\n" 
        f"[ = ] 𝗣𝗗𝗙 𝗳𝗶𝗹𝗲 𝗰𝗼𝗻𝘁𝗮𝗶𝗻𝘀 {count_images(valid_image_urls)} Images.\n\n" 
        "──────── ꌗꃅꍟꍟꉣꀘꍟꍟꉣꌗ ─────────"
    )



    # Send the PDF file to the user
    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(merged_pdf_path, 'rb'), caption=temp_message)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=query.message.message_id)
    # Remove the valid image files
    for img in valid_images:
        if os.path.exists(img):
            os.remove(img)  # Remove each image file    

    # Check and remove the merged PDF file
    if os.path.exists(merged_pdf_path):
        os.remove(merged_pdf_path)  # Remove the merged PDF file    

    # Finally, remove the user-specific folder and all of its contents
    if os.path.exists(user_folder):
        try:
            shutil.rmtree(user_folder)  # Remove the directory with all contents
        except OSError as e:
            print(f"Error deleting directory {user_folder}: {e}")



# Callback query handler for fetching images
async def handle_fetch_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    input_link = context.user_data.get('input_link')
    api_key = context.user_data.get('api_key')
    api_endpoint = context.user_data.get('api_endpoint')

    if not input_link or not api_endpoint:
        await query.message.reply_text("Missing information. Please try again.")
        return

    # Fetch images from the API
    api_response = requests.get(api_endpoint)
    if api_response.status_code != 200:
        await query.message.reply_text("Failed to retrieve images from the API.")
        return

    image_metadata = api_response.json()  # Get the full JSON response

    # Get image links using the new function
    valid_image_urls = get_image_links(image_metadata)

    if not valid_image_urls:
        await query.message.reply_text("No valid image URLs found.")
        return
    

    # Inform the user that fetching images is in progress
    fetching_status = "───────── ꌗꃅꍟꍟꉣꀘꍟꍟꉣꌗ ─────────\n\n[ # ] 𝗙𝗲𝘁𝗰𝗵𝗶𝗻𝗴 𝗜𝗺𝗮𝗴𝗲𝘀...\n\n── ꌗꃅꍟ ꉓꃅꂦꌗꍟ ꌗꂦꂵꍟꂦꈤꍟ ꍟ꒒ꌗꍟ (˚ ˃̣̣̥⌓˂̣̣̥) ──"
    fetching_status = await context.bot.edit_message_text(text=fetching_status, chat_id=update.effective_chat.id, message_id=query.message.message_id)
    
    # Delete the user's original message to keep the chat clean
    #await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=query.message.message_id)

    # Loop through the valid image URLs and download them
    for idx, img_url in enumerate(valid_image_urls):
        image_data = download_image(img_url)
        if image_data:
            # Send each downloaded image
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_data)

            # Prepare and send the uploaded message
            uploaded_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"[ + ] Image {idx + 1} uploaded.\n\n────── ꂵꀤꌗꌗ ꌩꂦꀎ ꀭꀎ꒒ꀤ (╥﹏╥) ──────")

            # Delete the fetching status message
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=fetching_status.message_id)

            # Update the fetching status to the latest message ID for deletion
            fetching_status = uploaded_message
        else:
            # Handle failure to download
            failed_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"[ - ] Failed to download image from {img_url}.\n\n────── ꍟꈤꀭꂦꌩ ꌩꂦꀎꋪ ꒒ꀤꎇꍟ ──────")

            # Delete the fetching status message
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=fetching_status.message_id)

            # Update the fetching status to the latest message ID for deletion
            fetching_status = failed_message


    #formatted_date from api call
    image_metadata = api_response.json()  # Get the full JSON response
    formatted_date = format_date_from_name(image_metadata['name'])
    valid_image_urls = get_image_links(image_metadata)

    text = ( 
        "──────── ꉣꀸꎇ ꌗꀎꂵꂵꍏꋪꌩ ────────\n\n" 
        f"[ # ] 𝗢𝗿𝗶𝗴𝗶𝗻𝗮𝗹 𝗟𝗶𝗻𝗸: {input_link}\n" 
        f"[ # ] 𝗔𝗽𝗶 𝗞𝗲𝘆: {api_key}\n\n" 
        f"[ # ] 𝗡𝗼𝘁𝗲𝘀 𝗖𝗿𝗲𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲: {formatted_date}\n"
        f"[ # ] 𝗣𝗗𝗙 𝗖𝗿𝗲𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲: {datetime.now().strftime('%d-%m-%Y')}\n" 
        f"[ # ] 𝗣𝗗𝗙 𝗳𝗶𝗹𝗲 𝗰𝗼𝗻𝘁𝗮𝗶𝗻𝘀: {len(valid_image_urls)} Images\n\n" 
        "────── ꅏꍟ ꂵꍟ꓄ ꀤꈤ 10꓄ꃅ ( ˶°ㅁ°) !! ──────" 
    )

    # Delete the last image uploaded message before sending the summary
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=fetching_status.message_id)
    # Send the final summary message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        # Delete the last image uploaded message before sending the summary
    




#help menu
async def help_command(update: Update, context):
    # Help message explaining how to use the bot
    help_message = (
        "📋 *𝗛𝗼𝘄 𝘁𝗼 𝗨𝘀𝗲 𝗦𝗵𝗲𝗲𝗽𝗞𝗲𝗲𝗽𝘀 𝗕𝗼𝘁* 🐑\n\n"
        "[ 1 ] /𝘀𝘁𝗮𝗿𝘁 - Start the bot and see basic information.\n"
        "[ 2 ] /𝘂𝗽𝗹𝗼𝗮𝗱 - Upload your notes to keep them safe.\n"
        "[ 3 ] /𝗴𝗲𝘁 - Retrieve your stored notes by using commands like `/getnote <note_name>`.\n"
        "[ 4 ] /𝗱𝗼𝗻𝗮𝘁𝗲 - Help the bot grow by making a donation!\n\n"
        "If you have any questions, check out the GitHub repository for the source code and more details.\n\n"
        "───────── ꌗꃅꍟꍟꉣꀘꍟꍟꉣꌗ ─────────"
    )

    # Create the inline button for GitHub
    keyboard = [[InlineKeyboardButton("GitHub Repo", url="https://github.com/your-repo-url")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the help message with the GitHub button
    await update.message.reply_text(help_message, reply_markup=reply_markup, parse_mode='Markdown')


# Main function to set up the bot
def main():
    application = ApplicationBuilder().token(bot_token).build()

    # Set up conversation handler

    application.add_handler(CommandHandler("start", start))
   #
    #application.add_handler(CallbackQueryHandler(button))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, export_admins))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_image))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_pdf_download))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_image_download))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_image_upload))
    application.add_handler(CommandHandler("help", help_command))
    #application.add_handler(CommandHandler("settings", settings))
    #application.add_handler(CallbackQueryHandler(button))
    #application.add_handler(CommandHandler("add_admin", add_admin))

    application.add_handler(CommandHandler('tmp', handle_image_upload))
    application.add_handler(CallbackQueryHandler(handle_download_pdf, pattern='download_pdf'))
    application.add_handler(CallbackQueryHandler(handle_fetch_images, pattern='fetch_images'))


    #application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), add_admin))
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

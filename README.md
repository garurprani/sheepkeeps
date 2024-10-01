<h1>SheepKeeps: Convert Note 5 URLs to PDF</h1>

<h2>Description</h2>
<p>The SheepKeeps Telegram bot enables users to convert Note 5 URLs into downloadable PDF files. This process involves a few key steps, including converting the user-provided URL to an API endpoint, fetching data, downloading images, generating a PDF, and sharing the file through Google Drive or directly via Telegram.</p>

<h2>Official Bot/channel</h2>
<p>> https://t.me/Sheepkeeps_bot</p>
<p>> https://t.me/sheepkeeps</p>

<h2>Features</h2>
<ul>
    <li><strong>Link Conversion:</strong> Converts Note 5 URLs into API endpoints for data retrieval.</li>
    <li><strong>Image Downloading:</strong> Downloads images associated with the Note 5 URL.</li>
    <li><strong>PDF Creation:</strong> Converts downloaded images into a single PDF file.</li>
    <li><strong>Google Drive Integration:</strong> Upload the generated PDF to Google Drive and receive a shareable link.</li>
    <li><strong>Direct Telegram Sharing:</strong> Send the generated PDF directly to the user’s Telegram chat.</li>
    <li><strong>User-friendly Interface:</strong> Utilizes inline buttons for easy user interaction.</li>
</ul>


<h2>URL Conversion:</h2>
<p>
The bot extracts the relevant ID from the provided Note 5 URL. For example, from the URL:

<code>http://air.ifpshare.com/documentPreview.html?s_id=08561e76-1f81-4b0b-a0c7-76bc5b4f1327</code>

Then bot identifies the s_id parameter value (08561e76-1f81-4b0b-a0c7-76bc5b4f1327).
It then constructs the API endpoint using this ID:

<code>https://air.ifpshare.com/api/shares/08561e76-1f81-4b0b-a0c7-76bc5b4f1327</code>
</p>

<h2>Requirements</h2>
<ul>
    <li>Python 3.x</li>
    <li>Required Python libraries:
        <ul>
            <li><code>requests</code></li>
            <li><code>google-auth</code></li>
            <li><code>google-api-python-client</code></li>
            <li><code>python-telegram-bot</code></li>
            <li><code>Pillow</code></li>
        </ul>
    </li>
    <li>Google Drive API credentials (if using Google Drive option)</li>
</ul>

<h2>Installation</h2>
<ol>
    <li><strong>Clone the repository:</strong>
        <pre><code>git clone https://github.com/garurprani/sheepkeeps.git
cd sheepkeeps</code></pre>
    </li>
    <li><strong>Install the required packages:</strong>
        <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Set up Google Drive API:</strong>
        <ul>
            <li>Create a project in the <a href="https://console.developers.google.com/" target="_blank">Google Developer Console</a>.</li>
            <li>Enable the Google Drive API.</li>
            <li>Create credentials (Service Account) and download the JSON file.</li>
            <li>Place the JSON file in the project directory and rename it to <code>credentials.json</code></li>
        </ul>
    </li>
</ol>

<h2>Usage</h2>
<ol>
    <li>Start the Telegram bot:
        <pre><code>python bot.py</code></pre>
    </li>
    <li>Use the <code>/start</code> command to initiate the bot.</li>
    <li>To upload a Note 5 URL to Google Drive, use:
        <pre><code>/upload &lt;Note 5 URL&gt;</code></pre>
        The bot will respond with a link to access the PDF on Google Drive.</li>
    <li>To send the PDF directly to your Telegram chat, use:
        <pre><code>/tmp</code></pre>
        The bot will process the request and send the PDF.</li>
</ol>

<h2>Example</h2>
<ol>
    <li>
        <strong>Upload a Note 5 URL:</strong> You can send either of the following commands to upload a Note 5 URL:
        <ul>
            <li>Using the direct document preview link:
                <pre>upload http://air.ifpshare.com/documentPreview.html?s_id=08561e76-1f81-4b0b-a0c7-76bc5b4f1327</pre>
            </li>
            <li>Or, use a detailed link:
                <pre>http://air.ifpshare.com/documentPreview.html?s_id=08561e76-1f81-4b0b-a0c7-76bc5b4f1327#/detail/63602dd6-1fc4-4feb-b099-d4a6d07a7ee2/record</pre>
            </li>
        </ul>
    </li>
    <li>
        <strong>Google Drive Upload:</strong> The bot will process the URL and upload the associated images as a PDF to Google Drive, then share a shareable link with you via Telegram.
      <pre>/upload http://air.ifpshare.com/documentPreview.html?s_id=08561e76-1f81-4b0b-a0c7-76bc5b4f1327#/detail/63602dd6-1fc4-4feb-b099-d4a6d07a7ee2/record</pre>
    </li>
    <li>
        <strong>Direct PDF Sending:</strong> If you want the PDF file to be sent directly to your chat, simply type:
        <pre>/upload http://air.ifpshare.com/documentPreview.html?s_id=08561e76-1f81-4b0b-a0c7-76bc5b4f1327#/detail/63602dd6-1fc4-4feb-b099-d4a6d07a7ee2/record</pre>
        </li>
  The bot will upload and send the PDF file directly to you on Telegram.
    </li>
</ol>

<h2>Contributing</h2>
<p>Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug reports.</p>

<h2>License</h2>
<p>This project is licensed under the MIT License.</p>

<h2>Contact</h2>
<p>Contact me anytime on telegram, but will mostly offline due to jee preparation</a>.</p>

</body>

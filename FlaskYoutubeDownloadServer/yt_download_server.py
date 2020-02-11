import io
import pathlib
import zipfile

from flask import Flask, request, send_file

import yt_downloader


app = Flask(__name__)
ip = '127.0.0.1'
port = 1337


@app.route('/')
def index():
    return (f'''
        <html>
            <body>
                <form action="http://{ip}:{port}/download" method="post">
                    <input type="submit" name="Absenden"><br>
                    <p>URL List:</p>
                    <textarea name="urllist" cols="60" rows="35"></textarea>
                </form>
            </body>
        </html>
    ''')


@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':

        url_list_unconverted = request.form['urllist']
        yt_downloader.create_download_list(True, url_list_unconverted)
        yt_downloader.execute_download()
        # yt_downloader.folder_to_zip('tmp')

        base_path = pathlib.Path('./tmp/')
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in base_path.iterdir():
                z.write(f_name)
        data.seek(0)
        for file in base_path.iterdir():
            yt_downloader.delete_file(file)
        return send_file(
            data,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='downloaded_songs.zip'
        )


@app.route('/download/json', methods=['POST'])
def json_download():
    req_data = request.get_json()

    encoder = req_data['encoder']
    url_list = req_data['url_list']

    yt_downloader.execute_json_download(url_list)
    # yt_downloader.folder_to_zip('tmp')

    base_path = pathlib.Path('./tmp/')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='downloaded_songs.zip'
    )




@app.route('/download/video', methods=['GET'])
def api_url():
    if 'url' in request.args:
        url = request.args['url']
    else:
        return 'Error: Keine URL angegeben. Bitte definiere eine URL.'

    yt_downloader.download_video(url)

    return 'Fertig heruntergeladen'


@app.route('/write/download_list', methods=['GET'])
def write_download_list():
    if 'url_list' in request.args:
        url_list = request.args['url_list']
    else:
        return 'Error: Es konnte keine Download Liste erstellt werden.'

    yt_downloader.create_download_list(True, url_list)

    return url_list
    # return 'Download Liste wurde erstellt'


if __name__ == '__main__':
    app.run(host=ip, port=port, debug=True)

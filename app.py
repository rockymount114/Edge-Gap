import os
import tempfile
from flask import Flask, request, render_template, send_file
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

column_widths = [2, 5, 12, 25, 4, 3, 2, 4, 6, 6, 15, 8, 8, 25, 20, 20, 3, 3, 1, 25, 20, 20, 3, 3, 1, 25, 25, 20, 2, 9, 25, 25, 20, 2, 9, 25, 25, 20, 2, 9, 8, 4, 8, 8, 6, 3, 3, 1, 3, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 15, 25, 20, 20, 3, 4, 25, 25, 20, 2, 9, 25, 20, 20, 3, 4, 25, 25, 20, 2, 9, 25, 20, 20, 3, 4, 25, 25, 20, 2, 9, 9, 1, 9, 4, 1, 1, 10, 1, 1, 2, 29, 6, 54, 10, 10, 10]

def convert_to_csv(folder_path):
    all_dataframes = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_fwf(file_path, widths=column_widths, header=None)
            all_dataframes.append(df)

    if not all_dataframes:
        raise ValueError("No DataFrames to concatenate. Please check the data source.")

    final_dataframe = pd.concat(all_dataframes, ignore_index=True)
    return final_dataframe

@app.route('/', methods=['GET', 'POST'])
def upload_folder():
    if request.method == 'POST':
        if 'folder' not in request.files:
            return 'No folder part'
        folder = request.files.getlist('folder')
        if not folder or folder[0].filename == '':
            return 'No selected folder'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in folder:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(temp_dir, filename))
            
            try:
                df = convert_to_csv(temp_dir)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_output:
                    output_path = temp_output.name
                    df.to_csv(output_path, index=False, header=False)  # Save without headers
                
                return_value = send_file(
                    output_path,
                    as_attachment=True,
                    download_name='output.csv',
                    mimetype='text/csv'
                )
                
                @return_value.call_on_close
                def delete_file():
                    os.remove(output_path)
                
                return return_value
            
            except Exception as e:
                return str(e)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
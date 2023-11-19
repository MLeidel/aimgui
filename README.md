# aimgui
### AI Image generation and variation desktop GUI

#### OpenAI v1.3.3 API with dall-e-2|3

aimgui.py is a desktop implementation of the openai API found at:

https://platform.openai.com/docs/api-reference/images/create-edit

It's a Python program that should be compatible with all the major
operating systems. By specifying a _prompt_ and an output image 
file location, you can gererate AI images. In addition, you can
specify for the output to go to your default web browser or
to files or both. Furthermore, you can run image variation
on an existing image file (with no prompt.)

A log file is updated with _prompt_ and image file names.  
Edit the aimgui.ini file to set default values.

256x256 | 512x512 | 1024x1024  
These are the only image file sizes allowed for this model.

![aimgui desktop app](images/aimgui.png "aimgui.py")

Before using this application Python 3.x must be installed.

Use Python >=3.7.1  
_make sure you're using the latest __OpenAI__ module_ v1.3.3


Use the requirements.txt file to install any modules you may be missing.

```bash
pip3 install -r requirements.txt
or
pip install -r requirements.txt
```

You will also have to Sign Up at https://openai.com/api/ and create an API Key.
There is no cost to do so.

Before using the program you will need to set up an Environment Variable 
called 'GPTKEY' whoes value will be your OpenAI API Key.

---


# Project Name: Django Cryptocurrency Price Prediction Web Application

## Overview
This project is a web application that enables users to predict cryptocurrency prices using the Django framework and utilizes tailwind CSS for styling. The core forecasting functionality is powered by the "Neural Prophet" library. More information about Neural Prophet can be found in the official documentation [here](https://nixtla.github.io/neuralforecast/).

## Getting Started
Follow the instructions below to set up and run the project on UNIX devices.

### Prerequisites
- Python 3.x
- Django
- Neural Prophet
- Tailwind CSS

### Installation
1. Clone the repository from GitHub.

```bash
git clone https://github.com/roughyy/Crypt.git
```

2. Install the required Python packages using pip.

```bash
pip install -r /path/to/requirements.txt
```

3. Edit the `forecast.py` file to modify the `set_posix_windows()` function for UNIX devices.

```python
    with set_posix_windows(): #just remove or comment this part of the code 
        model = torch.load(model_path)
```

### Running the Project
1. Navigate to the project directory.

```bash
cd your-project-directory
```

2. Start the Django development server.

```bash
python manage.py runserver
```

3. Access the web application in your web browser at `http://localhost:8000/`.

## Final Project at University
This project was developed as the final project for the University. You can find more detailed information about the project and its documentation on the University's website at [https://kc.umn.ac.id/26151/](https://kc.umn.ac.id/26151/).

## Contact Information
If you have any questions or feedback regarding the project, feel free to email me at muhammad.rafii.haditomo@gmail.com. I would be happy to assist you.


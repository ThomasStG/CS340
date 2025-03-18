# Installation Guide

## Windows

### Install npm and Node.js

#### Option 1: Use nvm (Node Version Manager)

1. Download **nvm for Windows**: [GitHub Releases](https://github.com/coreybutler/nvm-windows/releases)
2. Run `nvm_setup.exe` and follow the installation steps.
3. Install Node.js version 18.13:
   ```sh
   nvm install 18.13
   nvm use 18.13
   ```

### Clone the Project

```sh
git clone https://github.com/ThomasStG/CS340.git
```

### Navigate to the Directory

```sh
cd CS340/IDEAr
```

### Install Dependencies

```sh
npm install
```

Now you are ready to run the project!

---

## Python Virtual Environment

To ensure consistency, it's recommended to use a virtual environment for Python.

### Create a Virtual Environment

```sh
cd ..
python3 -m venv venv
```

### Activate the Virtual Environment

- **Mac/Linux**:
  ```sh
  source venv/bin/activate
  ```
- **Windows (Command Prompt)**:
  ```sh
  venv\Scripts\activate
  ```
- **Windows (PowerShell)**:
  ```sh
  venv\Scripts\Activate.ps1
  ```

### Install Python Dependencies

```sh
pip install -r requirements.txt
```

---

## Tailwind CSS Guide

To set up Tailwind with Vite:

```sh
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

For more details, check the [Tailwind CSS Documentation](https://tailwindcss.com/docs/installation/using-vite).

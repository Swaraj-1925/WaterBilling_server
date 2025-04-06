

# 💧 Water Meter Billing for Yashada Industry - Server
*VIIT 3rd Year Project (2024–25)*

---

## 🐍 Set Up Python Environment

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ☁️ Azure Setup Instructions

### 1. Computer Vision API

1. Create a **Computer Vision** resource in your Azure **Resource Group**.
2. Select the **Free pricing tier (F0)** for development/testing. You can upgrade later for production use.
3. Once created, go to the resource and copy:
   - `API_KEY`
   - `ENDPOINT`
4. Add these values to your `.env` file using the variable names provided in `env.sample`.

### 2. Storage Account

1. In the same **Resource Group**, create a new **Storage Account**.
2. Use mostly default settings, but update the following:
   - **Network Access**: Enable public access from *all networks*.
   - **Secure Transfer**: *Uncheck* “Require secure transfer for REST API operations”.
   - **Access Tier**: Set to `Cool` for lower-cost storage.
   - **Primary Service**: Choose either `Azure Blob Storage` or `Data Lake Storage Gen2`.
   - **Redundancy**: Select `LRS` (Locally Redundant Storage) — you can change this later if load increases.

### 3. Blob Container Configuration

1. Inside your storage account, create a container named:
   ```text
   bill-img
   ```
2. In the container settings, create a **Shared Access Signature (SAS)** token with the following permissions:
   - **Allowed Protocols**: HTTPS and HTTP
   - **Permissions**: Read, Write, Add, Create, List, Delete, Move

---

## 📦 Install Azure Image Analysis SDK

Ensure your virtual environment is active, then run:

```bash
pip install azure-ai-vision-imageanalysis
```

---

## 🚀 Run the App

Start the FastAPI server with:

```bash
fastapi dev main.py
```

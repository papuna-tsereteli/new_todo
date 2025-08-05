# React Native To-Do App

A simple and sleek to-do list application built with React Native and Expo.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, make sure you have the following installed on your computer:

* **Node.js** (LTS version is recommended). You can download it from [nodejs.org](https://nodejs.org/).
* **Git** for version control. You can get it from [git-scm.com](https://git-scm.com/).
* **A code editor** like Visual Studio Code.

### Installation & Setup

**1. Clone the Repository**

First, clone the repository to your local machine. Open your terminal or command prompt and run:

```bash
git clone <repository-url>
```
*(Replace `<repository-url>` with the actual URL of the project's repository.)*

Then, navigate into the newly created project directory:
```bash
cd <project-directory-name>
```
**2. .env**

 Create a file named `.env` in the root of the project directory.


    ```env
    API_URL=http://ur_ip:8000
    ```

**3. Install Dependencies**

Once you are inside the project directory, install all the necessary NPM packages.

```bash
npm install
```
*(If you use Yarn, you can run `yarn install` instead.)*

**4. Start the Development Server**

With the dependencies installed, start the Expo development server. This server bundles the JavaScript code and makes it available to the Expo Go app.

```bash
npx expo start
```
This will display a **QR code** in your terminal and open the Expo Developer Tools in a new browser tab.

**5. Run the App on Your Phone**

Now you can run the application on your physical device.

1.  **Install Expo Go:** If you haven't already, go to the App Store (for iOS) or Google Play Store (for Android) and install the **Expo Go** app.

2.  **Connect to the Same Network:** Ensure your computer and your mobile phone are connected to the **same Wi-Fi network**. This is crucial for them to communicate.

3.  **Scan the QR Code:**
    * Open the Expo Go app on your phone.
    * Select the "Scan QR Code" option.
    * Point your phone's camera at the QR code displayed in your computer's terminal or in the browser tab that opened.

The Expo Go app will then connect to the development server, and the To-Do app will appear on your phone's screen. Any changes you make to the code will automatically update in the app.

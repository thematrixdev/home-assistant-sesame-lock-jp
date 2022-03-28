# Sesame-Lock JP-Version Home-Assistant Custom-Component

If you have purchased your Sesame-Lock outside Japan, please use this:

https://www.home-assistant.io/integrations/sesame/

## Prerequisite
- Sesame Lock (for sure)
- Sesame WIFI module
- A pin (to reset the Lock)
- Android Studio
- An Android phone (emulator may work?)

## Setup Sesame Lock
- Install and power-on both Sesame-Lock and Sesame-WIFI-module
- Install the app and setup both the Lock and the WIFI-module
https://play.google.com/store/apps/details?id=co.candyhouse.sesame2
- In the app, sign-up a Sesame account

## Accquire Sesame API-Key
- https://partners.candyhouse.co/login

## Accquire Sesame Secret (private-key)
Please follow either one of the below method
- A. QR-Code-method
- B. Dev-App-method

### A. QR-Code-method
- Open Sesame-App on your phone
- Select the Lock, and choose properties
- "Share" the lock and get the QR-code

#### A1. Use any QR-Code Reader
- Scan and get the value of `sk`
- `base64` decode `sk`
- from 1st to 16th byte is the private-key

#### A2. Use an online Sesame-QR-Code Reader
- The QR-code-reader is not made by me. I bear no responsibility!
- https://sesame-qr-reader.vercel.app/
- Upload the QR-code image and get the data

### B. Dev-App-method
- Uninstall the Sesame-App from your phone
- Get Sesame Android app SDK (v2.0.7 at the time of writing this readme)
```
cd ~/
git clone https://github.com/CANDY-HOUSE/SesameSDK_Android_with_DemoApp.git
```
- Open the project with Android Studio
- Locate `app/java/co/candyhouse.app/App.kt`
- Place your `API-KEY` in `onCreate()`
```
class CandyHouseApp : Application() {
    override fun onCreate() {
        // original code here
        
        // MAKE SURE THIS LINE EXIST
        CHConfiguration.API_KEY = "X"
    }
}
```
- Locate any method with `device` and print out the Secret
. For example, `app/java/co/candyhouse.app/tabs/devices/model/CHDeviceViewModel.kt`
```
override fun onBleDeviceStatusChanged(device: CHSesameLocker, status: CHSesame2Status, shadowStatus: CHSesame2ShadowStatus?) {
    // original code here
    
    if (device.deviceStatus == CHSesame2Status.ReceivedBle) {
        device.connect {
            Log.d("sesame2SecretKey", device.getKey().secretKey)
        }
    }
}
```
- Connect your Android phone to Android Studio. Run the app
- Use the pin (the physical pin) to reset the Lock and the WIFI-Module
- Add the Lock and WIFI-Module in the app
- In Android Studio `Logcat`, search `sesame2SecretKey`. This is the Sesame-Secret
- Resetting the lock WILL RESET the secret!

## Accquire Sesame Lock UUID
- In the Android app, click on the Lock and locate it in the property page

## Install Home-Assistant Component
- Download `custom_components/sesame_jp` here
- SSH or SFTP into your Home-Assistant server
- Locate `configuration.yaml`
- Locate `custom_components` in the same directory. Create it if not exist 
- Put the downloaded `sesame_jp` into `custom_components`
- Restart Home-Assistant

## Configure Sesame-Lock in Home-Assistant
- Add these in `configuration.yaml`
```
lock:
  - platform: sesame_jp
    name: Sesame
    device_id: 'SESAME_UUID'
    api_key: 'SESAME_API_KEY'
    client_secret: 'SESAME_SECRET'
```
- Restart Home-Assistant

## Usage
- `Lock: Lock`
- `Lock: Unlock`

## Development environment
- Ubuntu 21.10
- Android 12 phone

## Testing environment
- Raspberry Pi 4B
- Raspbian Buster
- Home Assistant Container 2022.3.1 (i.e. Docker version)
- Sesame Lock 4
- Sesame WIFI-Module (For Sesame Lock 3 and 4)

## Resource
- Sesame Lock 4 https://jp.candyhouse.co/products/sesame4
- Sesame WIFI Module https://jp.candyhouse.co/products/new-wifi
- Sesame Web API https://doc.candyhouse.co/ja/SesameAPI
- Sesame Android SDK https://github.com/CANDY-HOUSE/SesameSDK_Android_with_DemoApp
- Obtain private-key from QR-Code https://qiita.com/kaonaga9/items/fb44d8e0b0aa93aab484
- Obtain private-key from QR-Code https://zenn.dev/key3/articles/6c1c2841d7a8a2

## Thanks
- Home Assistant community on Discord https://www.home-assistant.io/help/
- Google and Stackoverflow

# Sesame-Lock JP-Version Home-Assistant Custom-Component

If you have purchased your Sesame-Lock outside Japan, please use this:

https://www.home-assistant.io/integrations/sesame/

## Development environment
- Ubuntu 21.10
- Android 12 phone

## Tested environment
- Raspberry Pi 4B
- Raspbian Buster
- Home Assistant Container 2022.2.9 (i.e. Docker version)
- Sesame Lock 4
- Sesame WIFI-Module (For Sesame Lock 3 and 4)

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

## Resource
- Sesame Lock 4 https://jp.candyhouse.co/products/sesame4
- Sesame WIFI Module https://jp.candyhouse.co/products/new-wifi
- Sesame Web API https://doc.candyhouse.co/ja/SesameAPI
- Sesame Android SDK https://github.com/CANDY-HOUSE/SesameSDK_Android_with_DemoApp

## Thanks
- Home Assistant community on Discord https://www.home-assistant.io/help/
- Google and Stackoverflow
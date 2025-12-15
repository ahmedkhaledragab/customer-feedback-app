[app]

title = متابعة آراء العملاء

package.name = customerfeedback
package.domain = com.ahmedkhaled

source.dir = .
source.main = main.py

version = 1.0

requirements = python3,kivy==2.1.0,pyjnius

orientation = portrait
fullscreen = 0

android.api = 30
android.minapi = 21

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.include_sqlite3 = 1

android.entrypoint = org.kivy.android.PythonActivity
android.copy_libs = 1

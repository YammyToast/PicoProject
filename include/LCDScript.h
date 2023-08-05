#ifndef LCD_SCRIPT_H
#define LCD_SCRIPT_H

#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include "ImageData.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

int initialize_settings(UDOUBLE, UWORD*);

int opening_screen(void);

int main_menu(void);

enum window_state;

#endif
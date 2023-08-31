#ifndef LCD_SCRIPT_H
#define LCD_SCRIPT_H

#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

void opening_screen_update_callback(int*, UWORD*);

int initialize_settings(UDOUBLE, UWORD*);

int opening_screen(UWORD*);

int main_menu(UWORD*);

void render_frame(
    int,
    int,
    int,
    const float*,
    UWORD,
    UWORD);

enum window_state;

#endif
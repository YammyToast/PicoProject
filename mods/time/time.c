#include <stdio.h>
#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"
#include "time.h"
#include "calc.c"

#include "paintAPI.h"

#ifndef TIME_MAIN
#define TIME_MAIN

UWORD *BlackImage;

void display(UWORD* black_image) {
    Paint_DrawString_EN(8, 8, "TIME MODULE DISPLAY", &Font24, WHITE, RAISIN);
	LCD_2IN_Display((uint8_t * )black_image);     
    DEV_Delay_ms(1000);

    image_link image1 = {
         .ref = "./resizedimage.png",
         .width = 84,
         .height = 84 
    };
}
void thumbnail(UWORD* black_image) {
    int x = 0;
}
void settings(UWORD* black_image) {
    int x = 0;
}
void update(UWORD* black_image) {
    int x = 0;
}   


#endif
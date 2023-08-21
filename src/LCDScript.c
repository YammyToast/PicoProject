#ifndef LCD_SCRIPT
#define LCD_SCRIPT

#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include "ImageData.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

#include "LCDScript.h"
#include "ProjectConfig.h"

const int loading_bar_height = 16;

enum window_state {
    Opening = 0,
    MainMenu,


};


int initialize_settings(UDOUBLE _image_size, UWORD *_black_image) {
    DEV_Delay_ms(100);
    if(DEV_Module_Init()!=0){
        return -1;
    }
    DEV_SET_PWM(50);
    /* LCD Init */
    LCD_2IN_Init(HORIZONTAL);
    LCD_2IN_Clear(WHITE);
    
    LCD_2IN_SetBacklight(1);

    Paint_NewImage((UBYTE *)_black_image,LCD_2IN.WIDTH,LCD_2IN.HEIGHT, 90, WHITE);
    Paint_SetScale(65);
    Paint_Clear(RAISIN);
    Paint_SetRotate(ROTATE_270);


    return 0;
}

void opening_screen_update_callback(int* _percentage, UWORD* _black_image) {
        int percentage = *_percentage;
        int loading_bar_current = (LCD_2IN_WIDTH - 18) * (percentage) / 100;
        printf("Loading: %d, Bar-Length: %d\n", percentage, loading_bar_current);
        char cPercentage[16];
        snprintf(cPercentage, 16, "Percentage: %d", percentage);
        Paint_DrawString_EN(8, 64, cPercentage, &Font16, WHITE, RAISIN);
        
        Paint_DrawRectangle(
            9,
            LCD_2IN_HEIGHT - (6 + loading_bar_height),
            LCD_2IN_WIDTH - (9),
            LCD_2IN_HEIGHT - 8,
            RAISIN,
            1,
            1   
        );

        Paint_DrawRectangle(
            9,
            LCD_2IN_HEIGHT - (7 + loading_bar_height),
            (9 + loading_bar_current),
            LCD_2IN_HEIGHT - 8,
            GREEN,
            1,
            1   
        );
        LCD_2IN_Display((uint8_t * )_black_image); 

}

int opening_screen(UWORD* _black_image ) {
    char version[15];

    Paint_DrawString_EN(8, 8, "WaifuWatch", &Font24, WHITE, RAISIN);


    snprintf(version, 15, "Version: %d.%d", pico_main_VERSION_MAJOR, pico_main_VERSION_MINOR);
    Paint_DrawString_EN(8, 40, version, &Font16, WHITE, RAISIN);

    int percentage = 0;
        
    Paint_DrawRectangle(
        8,
        LCD_2IN_HEIGHT - (8 + loading_bar_height),
        LCD_2IN_WIDTH - 8,
        LCD_2IN_HEIGHT - 8,
        WHITE,
        1,
        DRAW_FILL_EMPTY
    );



    while(percentage <= 100) {
        opening_screen_update_callback(&percentage, _black_image);
        sleep_ms(1000);
        percentage = percentage + 20;

    }
    DEV_Delay_ms(1000);
    LCD_2IN_Display((uint8_t * )_black_image);     
    return 1;
}

int main_menu(UWORD* _black_image) {
    // Paint_DrawImage1(gImage_2inch_1,0,0,320,240);
    // UDOUBLE Imagesize = LCD_2IN_HEIGHT*LCD_2IN_WIDTH*2;
    // UWORD *BlackImage;

    // LCD_2IN_Display((UBYTE *)BlackImage);
    // DEV_Delay_ms(10);
            
    // Paint_DrawString_EN(8, 8, "Main Menu", &Font24, WHITE, RAISIN);
                
    // LCD_2IN_Display((uint8_t * )BlackImage);    

    Paint_DrawString_EN(8, 8, "MainMenu", &Font24, WHITE, RAISIN);
    LCD_2IN_Display((uint8_t * )_black_image);     
    return 1;

    
}



#endif
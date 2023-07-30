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


int initialize_settings(UDOUBLE _image_size, UWORD *_black_image) {
    DEV_Delay_ms(100);
    ("LCD_2in_test Demo\r\n");
    if(DEV_Module_Init()!=0){
        return -1;
    }
    DEV_SET_PWM(50);
    /* LCD Init */
    LCD_2IN_Init(HORIZONTAL);
    LCD_2IN_Clear(WHITE);
    
    LCD_2IN_SetBacklight(1);



    return 0;
}

void opening_screen(void) {
    char version[15];
    Paint_Clear(RAISIN);

    Paint_DrawString_EN(8, 8, "WaifuWatch", &Font24, WHITE, RAISIN);


    snprintf(version, 15, "Version: %d.%d", pico_main_VERSION_MAJOR, pico_main_VERSION_MINOR);
    Paint_DrawString_EN(8, 40, version, &Font16, WHITE, RAISIN);

    int percentage = 0;
    int loading_bar_height = 16;
    int loading_bar_current = 0;
        
    Paint_DrawRectangle(
        8,
        LCD_2IN_HEIGHT - (8 + loading_bar_height),
        LCD_2IN_WIDTH - 8,
        LCD_2IN_HEIGHT - 8,
        WHITE,
        1,
        DRAW_FILL_EMPTY
    );


    while(percentage < 100) {
        loading_bar_current = (LCD_2IN_WIDTH - 9) * (percentage / 100);

        char cPercentage[15];
        snprintf(cPercentage, 15, "Percentage: %d", percentage);
        Paint_DrawString_EN(8, 64, cPercentage, &Font16, WHITE, RAISIN);
        
        // Paint_DrawRectangle(
        //     9,
        //     LCD_2IN_HEIGHT - (6 + loading_bar_height),
        //     LCD_2IN_WIDTH - (9),
        //     LCD_2IN_HEIGHT - 8,
        //     RAISIN,
        //     1,
        //     1   
        // );

        // Paint_DrawRectangle(
        //     9,
        //     LCD_2IN_HEIGHT - (6 + loading_bar_height),
        //     (8 + percentage),
        //     LCD_2IN_HEIGHT - 8,
        //     RED,
        //     1,
        //     1   
        // );
        sleep_ms(10);
        percentage = percentage + 1;

    }
    DEV_Delay_ms(1000);

}

void runtime_main(void) {


}



#endif
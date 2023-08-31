#ifndef LCD_SCRIPT
#define LCD_SCRIPT

#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

#include "ImageDat.c"

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

void render_frame(
    int padding,
    int calculated_frame_width,
    int calculated_frame_height,
    const float* split_ratio,
    UWORD background_color,
    UWORD line_color
)
{
    // int calculated_frame_height = LCD_2IN_HEIGHT - (2 * padding);
    // int calculated_frame_width = LCD_2IN_WIDTH - (2 * padding);
    
    int image_frame_height = (int)(calculated_frame_height * *split_ratio);
    int widget_frame_height = (int)(calculated_frame_height * (1 - *split_ratio));
    // printf("IMAGE: %d\n", image_frame_height);

    int x, y;
    for(int i = 0; i < sizeof(personality_image) / sizeof(UWORD); i++) {
        x = padding + (i % 84);
        y = padding + widget_frame_height + (i / 84);
        Paint_DrawPoint(x, y, personality_image[i], 1, 0);
    }


    Paint_DrawRectangle(
        padding,
        padding + widget_frame_height,
        padding + calculated_frame_width,
        padding + widget_frame_height + image_frame_height,
        OUTLINE,
        1,
        DRAW_FILL_EMPTY
    );
    Paint_DrawLine(
        padding + image_frame_height,
        padding + widget_frame_height,
        padding + image_frame_height,
        padding + widget_frame_height + image_frame_height,
        OUTLINE,
        1,
        LINE_STYLE_SOLID
    );

    // Paint_DrawRectangle(
    //     padding,
    //     padding,
    //     padding + calculated_frame_width,
    //     padding + widget_frame_height,
    //     OUTLINE,
    //     2,
    //     DRAW_FILL_EMPTY
    // );

    Paint_DrawString_EN(
        padding * 2,
        padding * 2,
        "Widget Data",
        &Font24,
        TEXT,
        RAISIN);

    Paint_DrawString_EN(
        padding * 2 + image_frame_height,
        padding * 2 + widget_frame_height,
        "Personality Text",
        &Font16,
        TEXT,
        RAISIN);
    // Paint_DrawString_EN(
    //     padding * 2 + image_frame_height,
    //     padding * 2 + widget_frame_height + 16,
    //     "(Says something",
    //     &Font16,
    //     WHITE,
    //     RAISIN);
    // Paint_DrawString_EN(
    //     padding * 2 + image_frame_height,
    //     padding * 2 + widget_frame_height + 32,
    //     "hot)",
    //     &Font16,
    //     WHITE,
    //     RAISIN);


}

int main_menu(UWORD* _black_image) {
    Paint_DrawString_EN(8, 8, "MainMenu", &Font24, WHITE, RAISIN);
    LCD_2IN_Display((uint8_t * )_black_image);     
    return 1;

    
}



#endif
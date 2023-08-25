#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()

#ifndef CORE_PAINT_API_MAIN
#define CORE_PAINT_API_MAIN

void LCD_Clear(UWORD color) {
    Paint_Clear(UWORD color);

}

void LCD_ClearWindows(UWORD x1, UWORD y1, UWORD x2, UWORD y2, UWORD color) {
    Paint_ClearWindows(x1, y1, x2, y2, color);

}

//Drawing
void LCD_DrawPoint(UWORD x, UWORD y, UWORD color, DOT_PIXEL dot_pixel, DOT_STYLE dot_fill_style) {
    Paint_DrawPoint(x, y, color, dot_pixel, dot_fill_style);

}
void LCD_DrawLine(UWORD x1, UWORD y1, UWORD x2, UWORD y2, UWORD color, DOT_PIXEL line_width, LINE_STYLE line_style) {
    Paint_DrawLine(x1, y1, x2, y2, color, line_width, line_style);

}
void LCD_DrawRectangle(UWORD x1, UWORD y1, UWORD x2, UWORD y2, UWORD color, DOT_PIXEL line_width, DRAW_FILL draw_fill) {
    Paint_DrawRectangle(x1, y1, x2, y2, color, line_width, draw_fill);

}
void LCD_DrawCircle(UWORD x_center, UWORD y_center, UWORD radius, UWORD color, DOT_PIXEL line_width, DRAW_FILL draw_fill) {
    Paint_DrawCircle(x_center, y_center, radius, color, line_width, draw_fill);

}

//Display string
void LCD_DrawChar(UWORD x, UWORD y, const char ascii_char, sFONT* font, UWORD color_foreground, UWORD color_background) {
    Paint_DrawChar(x, y, ascii_char, dont, color_foreground, color_background);

}
void LCD_DrawString(UWORD x, UWORD y, const char * text, sFONT* font, UWORD color_foreground, UWORD color_background) {
    Paint_DrawString_EN(x, y, text, font, color_foreground, color_background);

}

#endif
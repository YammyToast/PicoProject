#include <stdio.h>
#include "pico/stdlib.h"

#include "DEV_Config.h"
#include "GUI_Paint.h"
#include "Debug.h"
#include <stdlib.h> // malloc() free()

#include "LCD_2in.h"

#ifndef TIME_H
#define TIME_H

void display(UWORD*);
void thumbnail(UWORD*);
void settings(UWORD*);
void update(UWORD*);

#endif
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

uint16_t bits = 0;

bool input0, input1, input2, input3, input4;
bool input5, input6, input7, input8, input9;
bool input10, input11, input12;

void setup() {
  // This is the Bluetooth name shown on your computer.
  SerialBT.begin("ESP32_Inputs");

  pinMode(2, INPUT_PULLDOWN);
  pinMode(4, INPUT_PULLDOWN);
  pinMode(5, INPUT_PULLDOWN);
  pinMode(18, INPUT_PULLDOWN);
  pinMode(19, INPUT_PULLDOWN);
  pinMode(21, INPUT_PULLDOWN);
  pinMode(22, INPUT_PULLDOWN);
  pinMode(23, INPUT_PULLDOWN);
  pinMode(12, INPUT_PULLDOWN);
  pinMode(14, INPUT_PULLDOWN);
  pinMode(27, INPUT_PULLDOWN);
  pinMode(26, INPUT_PULLDOWN);
  pinMode(33, INPUT_PULLDOWN);
}

void loop() {
  // Read the 13 inputs.
  input0  = digitalRead(2);
  input1  = digitalRead(4);
  input2  = digitalRead(5);
  input3  = digitalRead(18);
  input4  = digitalRead(19);
  input5  = digitalRead(21);
  input6  = digitalRead(22);
  input7  = digitalRead(23);
  input8  = digitalRead(12);
  input9  = digitalRead(14);
  input10 = digitalRead(27);
  input11 = digitalRead(26);
  input12 = digitalRead(33);

  // Store each input in its matching bit.
  bitWrite(bits, 0, input0);
  bitWrite(bits, 1, input1);
  bitWrite(bits, 2, input2);
  bitWrite(bits, 3, input3);
  bitWrite(bits, 4, input4);
  bitWrite(bits, 5, input5);
  bitWrite(bits, 6, input6);
  bitWrite(bits, 7, input7);
  bitWrite(bits, 8, input8);
  bitWrite(bits, 9, input9);
  bitWrite(bits, 10, input10);
  bitWrite(bits, 11, input11);
  bitWrite(bits, 12, input12);

  // Send all 13 digits over Bluetooth when connected.
  if (SerialBT.hasClient()) {
    for (int bit = 12; bit >= 0; bit--) {
      SerialBT.print(bitRead(bits, bit));
    }
    SerialBT.println();
  }

  delay(200);
}

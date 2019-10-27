#include "pins.h"

#include <VL53L0X.h>
#include <Wire.h>

// Invert encoder directions if needed
const boolean INVERT_ENCODER_LEFT = false;
const boolean INVERT_ENCODER_RIGHT = false;

// Invert motor directions if needed
const boolean INVERT_MOTOR_LEFT = false;
const boolean INVERT_MOTOR_RIGHT = false;

// Loop count, used for print statements
int count = 0;

// Sensor states
float velocity_angular = 0;
float velocity_linear = 0;
float left_dist;
float right_dist;
float center_dist;

//Lab 7 variables------------------------------------------------------
 double distance_past_wall = 0;
 double average_right_dist = 0;
 double current_right_dist = 0;
 double past_right_dist = 0;
 double average_left_dist = 0;
 double current_left_dist = 0;
 double past_left_dist = 0;

 int Direction_of_mouse = 0; //0 forward, 1 right, 2 down, 3 left, compared to original position
 int Mouse_x = 0;
 int Mouse_y = 0;
 bool Left_Turn = false;
 bool Right_Turn = false;
 

 struct Wall_var        //For information about the sqares around us
 {
  int Wall_x;
  int Wall_y;
  bool Left_wall = false;  //False means no wall
  bool Forward_wall = false;
  bool Right_wall = false;
  bool Back_wall = false;
  bool Traveled_Previous_Left = false; //Oriented if you are facing forward
  bool Traveled_Previous_Right = false;
  bool Traveled_Previous_Center = false;

  int value_of_square = 0; //For maze solving
 };

 Wall_var Map[5][5];



 
 
 //Lab 7 variables------------------------------------------------------

void setup() {
  Serial.begin(9600);
  hardwareSetup();

 for (int g = 0; g < 4; g++)
 {
   for (int f = 0; f < 4; f++)
    {
     Map[g][f].Wall_x = g;
     Map[g][f].Wall_y = f;
    }
 }


  Map[0][0].Wall_x = 0;  //Update first square as it would be in the Micromouse Competition 
  Map[0][0].Wall_y = 0;
  Map[0][0].Right_wall = true;
  Map[0][0].Left_wall = true;
  Map[0][0].Forward_wall = false;
  Map[0][0].Back_wall = true;
  
}

void loop() {
  // Read sensor data
  left_dist = getDistanceLeft();
  right_dist = getDistanceRight();
  center_dist = getDistanceCenter();

  velocity_linear = getLinearVelocity();
  velocity_angular = getAngularVelocity();

  filter_left_right_distance(); //OPTIONAL: modify this filter function

  ////////////////////////////////////
  // Your changes should start here //
  ////////////////////////////////////



  //Identify if there is an opening to the left or right, you may want to take an average of 2 or 3 distance readings if your robot wants to turn too often
  distance_past_wall = 22; //TODO:: Change this if needed

  if (left_dist > distance_past_wall)
    Left_Turn = true;
  else if (right_dist > distance_past_wall)
    Right_Turn = true;

  update_position();

  if (Left_Turn) //Turn Left
    {
      forward();
      turn(0);
      Direction_of_mouse -= 1; //left
    }
  else if (Right_Turn) //Turn Right
    {
      forward();
      turn(1);
      Direction_of_mouse += 1; //Right
    }
  else
  {
      forward();
      Direction_of_mouse += 0; //Forward
  }

  update_Wall_Var();
  Right_Turn = false;
  Left_Turn = false;

  

  // Print debug info every 500 loops
  if (count % 500 == 0) {
    //Serial.print(velocity_linear / 100.0);
    //Serial.print(" ");
    //Serial.print(velocity_angular);
    //Serial.print(" ");
    //Serial.print(left_dist);
    //Serial.print(" ");
    //Serial.print(center_dist);
    //Serial.print(" ");
    //Serial.print(right_dist);
    //Serial.println();
    Serial.print("[X value: ");
    Serial.print(Mouse_x);
    Serial.print(" , Y value: ");
    Serial.print(Mouse_y);
    Serial.print(" ]        Final Direction: ");
    Serial.print(Direction_of_mouse);
    Serial.println(" ");
  }
  count++;

  checkEncodersZeroVelocity();
  updateDistanceSensors();
}

void filter_left_right_distance(void) //OPTIONAL: Modify Filter Sensor Data------------------------------------------
{
  if (right_dist > 100) //If we get a bad really large number we will just replace it with our previous average so the later wall folowing error isnt huge and wrong
    right_dist = average_right_dist;
  if (left_dist > 100)
    left_dist = average_left_dist;

  if (right_dist < 10) //Our minimum value when there is nothing in front of the sensor will hover on some value under 10cm so we can set it to 0 to not confuse our wall follower when choosing which wall to follow
    right_dist = 0;
  if (left_dist < 10)
    left_dist = 0;
  
  past_right_dist = current_right_dist; //sets past dist to right distance from last loop
  current_right_dist = right_dist;      //sets the variable to updated right distance
  past_left_dist = current_left_dist;
  current_left_dist = left_dist;
   
  average_right_dist = (past_right_dist + current_right_dist) / 2; //Average of last two right distance values, can be increased to average last 3 or 4 values if you add more past variables
  average_left_dist = (past_left_dist + current_left_dist) / 2;
 }



void update_position(void)
{
  //Direction_of_mouse 0 forward, 1 right, 2 down, 3 left, compared to original position
  if (Direction_of_mouse == 0)
  {
    Mouse_x += 0;
    Mouse_y += 1;
  }

  if (Direction_of_mouse == 1)
  {
    Mouse_x += 1;
    Mouse_y += 0;
  }

  if (Direction_of_mouse == 2)
  {
    Mouse_x += 0;
    Mouse_y += -1;
  }

  if (Direction_of_mouse == 3)
  {
    Mouse_x += -1;
    Mouse_y += 0;
  }
}

void update_Wall_Var(void)
{
//Hint: make sure you use the direction of the mouse when updating the details of the square in front of the mouse
//Hint: Since our mouse should just move forward the first move, update the x and y of Move1 as x = 0 and y = 1
//Hint: should use code similar to the code in the setup function, for each move variable, use ForwardCount to keep track of which move to update
//Hint: You'll probably need a lot of If statements
//Hint: You only update after you move, or move and turn
//Hint: Update mouse position too Wall_x , Wall_y

 if (Direction_of_mouse == -1)
 {
   Direction_of_mouse = 3;
 }

 if (Direction_of_mouse == 4)
 {
   Direction_of_mouse = 0;
 }


 if (Direction_of_mouse == 0) //Observing walls od square in front of new mouse location
  {
    Map[ Mouse_x + 0 ][ Mouse_y + 1 ].Left_wall = observe_Wall(0);
    Map[ Mouse_x + 0 ][ Mouse_y + 1 ].Right_wall = observe_Wall(1);
    Map[ Mouse_x + 0 ][ Mouse_y + 1 ].Forward_wall = observe_Wall(2);

  }

  if (Direction_of_mouse == 1)
  {
    Map[ Mouse_x + 1 ][ Mouse_y + 0 ].Forward_wall = observe_Wall(0);
    Map[ Mouse_x + 1 ][ Mouse_y + 0 ].Back_wall = observe_Wall(1);
    Map[ Mouse_x + 1 ][ Mouse_y + 0 ].Right_wall = observe_Wall(2);
  }

  if (Direction_of_mouse == 2)
  {
    Map[ Mouse_x + 0 ][ Mouse_y + -1 ].Right_wall = observe_Wall(0);
    Map[ Mouse_x + 0 ][ Mouse_y + -1 ].Left_wall = observe_Wall(1);
    Map[ Mouse_x + 0 ][ Mouse_y + -1 ].Back_wall = observe_Wall(2);
  }

  if (Direction_of_mouse == 3)
  {
    Map[ Mouse_x + -1 ][ Mouse_y + 0 ].Back_wall = observe_Wall(0);
    Map[ Mouse_x + -1 ][ Mouse_y + 0 ].Forward_wall = observe_Wall(1);
    Map[ Mouse_x + -1 ][ Mouse_y + 0 ].Left_wall = observe_Wall(2);
  }
}

bool observe_Wall(int LOR) //LOR == 0 left     LOR == 1 right       LOR == 2 center
{
  updateDistanceSensors();
  left_dist = getDistanceLeft();
  right_dist = getDistanceRight();
  center_dist = getDistanceCenter();

  if (LOR == 0)
  {
    if (left_dist < distance_past_wall)
    {
      return true;
    }
    else 
    {
      return false;
    }
  }

  if (LOR == 1)
  {
    if (right_dist < distance_past_wall)
    {
      return true;
    }
    else 
    {
      return false;
    }
  }

  if (LOR == 2)
  {
    if (right_dist < 30)  //TODO change this if needed
    {
      return true;
    }
    else 
    {
      return false;
    }
  }
  
}
  




void turn(int direct)  //TODO  direct = 0 means turn left, direct = 1 means turn right
{

   resetEncoderCounts(); //resets functions returnRightEncoderDistance() and returnLeftEncoderDistance() if you want to use them for controlled turn

   
  //Make 90 degree turn, if direct equals 0 turn left, if 1 turn right
  //We reccomend you use functions returnRightEncoderDistance() and returnLeftEncoderDistance()
  //A loop and applyPowerLeft("") and applyPowerRight("") with at least a proportional controller(like angular controller) keeping the wheel turning in oppoiste directions at same speed would be useful 

  applyPowerLeft(0); //Stop so we can turn in place
  applyPowerRight(0);
  delay(20);
  
  double turn_right_power = 0.4;
  double turn_left_power = -0.4;
  double turn_error = 0;
  double turn_P = 0;

  resetEncoderCounts();
  


  //OPTIONAL:: Make the robot drive a certain distance forward if needed for distance sensors to work correctly
}

void forward(void) //TODO
{
  double x_distance = 16; //TODO

  resetEncoderCounts(); //Resets functions returnRightEncoderDistance() and returnLeftEncoderDistance()
  
  // Go forward by x_distance
  //You can use returnRightEncoderDistance() and returnLeftEncoderDistance() to get the distance each wheel has gone and take average
  //You can also use velocity linear and micros like the old labs if you do not want to use returnRightEncoderDistance() and returnLeftEncoderDistance()



    

}

void deadend(void) //TODO how to get out of a dead end and try not to end back up into a dead end
{
}


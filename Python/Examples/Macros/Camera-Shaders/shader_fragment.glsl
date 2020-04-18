#ifdef GL_FRAGMENT_PRECISION_HIGH
#define maxfragp highp
#else
#define maxfragp medp
#endif

#ifdef GL_ES
precision maxfragp int;
precision maxfragp float;
#endif

// Color provided by RoboDK for each draw set
uniform vec4 Color;

// Modelview matrix
uniform mat4 ModelView;

// calculated vertex and normal from the vertex shader
varying vec3 eyeVertex;
varying vec3 eyeNormal;

void main(void)  {
    // colors defined as RGBA (0-1)
    vec4 light_ambient_C = vec4(1,1,1 , 1);  // Color
    vec4 light_diffuse_C = Color;
    vec4 light_specular_C = Color;
    
    // light position (with respect to camera coordinates or it can be defined with respect to a coordinate system in RoboDK)
    // if the position is defined with respect to the RoboDK station, simply enter the XYZ coordinates of the position with respect to the station
    // more information here: https://robodk.com/doc/en/Basic-Guide.html#RefFrames
    vec3 light_Position = vec3(2000.0 , -1500.0 , 500.0);
    
    // define the position of the light with respect to the world coordinate system (not the camera)
    // in this case, the light is placed with respect to the RoboDK station reference
    // if you comment next line, the light coordinates will be given with respect to the camera
    light_Position = vec3(ModelView * vec4(light_Position, 1.0));    
    
    float kiamb = 0.2;
    float kidiff = 0.8;
    float kispec = 0.4;

    vec3 L = normalize(light_Position - eyeVertex);
    vec3 E = normalize(-eyeVertex); // we are in Eye Coordinates, so EyePos is (0,0,0)
    vec3 R = normalize(-reflect(L,eyeNormal));

    //calculate Ambient Term:
    float normal_light = dot(eyeNormal,L);
    vec4 Iamb = light_ambient_C;

    //calculate Diffuse Term:
    vec4 Idiff = light_diffuse_C * max(normal_light, 0.0);
    Idiff = clamp(Idiff, 0.0, 1.0);

    // Calculate Specular Term:
    //vec4 Ispec = light_specular_C * pow(max(dot(R,E),0.0),shininess);
    vec4 Ispec = light_specular_C * max(dot(R,E),0.0);
    Ispec = clamp(Ispec, 0.0, 1.0);
    
    // Calculate the final Color:
    gl_FragColor = clamp(kiamb*Iamb + kidiff*Idiff + kispec*Ispec, 0.0, 1.0);
    gl_FragColor[3] = Color[3];
    //gl_FragColor = Color;
}

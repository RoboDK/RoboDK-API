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
    float far_length = 2000.0;
    
    // Calculate the final Color:
    gl_FragColor = clamp(eyeVertex[2]/far_length, 0.0, 1.0);
    gl_FragColor[3] = Color[3];
    //gl_FragColor = Color;
}

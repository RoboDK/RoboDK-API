#ifdef GL_FRAGMENT_PRECISION_HIGH
#define maxfragp highp
#else
#define maxfragp medp
#endif

#ifdef GL_ES
precision maxfragp int;
precision maxfragp float;
#endif

// Attributes
attribute vec3 Vertex;
attribute vec3 Normal;

// Matrices (Projection and ModelView)
uniform mat4 Projection;
uniform mat4 ModelView;

// calculated vertex and normal from the vertex shader to the fragment shader
varying vec3 eyeVertex;
varying vec3 eyeNormal;

// enter distortion coefficients
float dist_coeffs[8] = float[](0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.);

// Apply distortion on a vertex using the rational model
vec4 distort(vec4 view_pos){
    // normalize
    float z = view_pos[2];
    float z_inv = 1 / z;
    float x1 = view_pos[0] * z_inv;
    float y1 = view_pos[1] * z_inv;
    // precalculations
    float x1_2 = x1*x1;
    float y1_2 = y1*y1;
    float x1_y1 = x1*y1;
    float r2 = x1_2 + y1_2;
    float r4 = r2*r2;
    float r6 = r4*r2;
    // rational distortion factor
    float r_dist = (1 + dist_coeffs[0]*r2 +dist_coeffs[1]*r4 + dist_coeffs[4]*r6) 
    / (1 + dist_coeffs[5]*r2 + dist_coeffs[6]*r4 + dist_coeffs[7]*r6);
    // full (rational + tangential) distortion
    float x2 = x1*r_dist + 2*dist_coeffs[2]*x1_y1 + dist_coeffs[3]*(r2 + 2*x1_2);
    float y2 = y1*r_dist + 2*dist_coeffs[3]*x1_y1 + dist_coeffs[2]*(r2 + 2*y1_2);
    // denormalize for projection (which is a linear operation)
    return vec4(x2*z, y2*z, z, view_pos[3]);
}

void main(void) {
    eyeNormal = vec3(ModelView * vec4(Normal, 0.0));
    eyeVertex = vec3(ModelView * vec4(Vertex, 1.0));

    // Calculate eye space normal
    gl_Position = Projection * distort(ModelView * vec4(Vertex,1.0));
}

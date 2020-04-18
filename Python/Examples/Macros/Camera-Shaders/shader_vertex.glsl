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

void main(void) {
    mat4 mat_mvp = Projection * ModelView;
    eyeNormal = vec3(ModelView * vec4(Normal, 0.0));
    eyeVertex = vec3(ModelView * vec4(Vertex, 1.0));

    // Calculate eye space normal
    gl_Position = mat_mvp * vec4(Vertex,1.0);
}


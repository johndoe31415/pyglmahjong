#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertex_ModelSpace;
layout(location = 1) in vec2 vertex_TexCoords;
layout(location = 2) in vec3 normal_ModelSpace;

// Output data ; will be interpolated for each fragment.
out vec2 texCoords;
out vec3 vertex_WorldSpace;
out vec3 normal_CameraSpace;
out vec3 eyeDir_CameraSpace;
out vec3 lightDir_CameraSpace;

// Values that stay constant for the whole mesh.
uniform mat4 modelViewProjMatrix;
uniform mat4 projMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;
uniform vec3 lightPos_WorldSpace;

void main(){
	// Output position of the vertex, in clip space : MVP * position
	gl_Position = modelViewProjMatrix * vec4(vertex_ModelSpace, 1);
	//gl_Position = projMatrix * viewMatrix * modelMatrix * vec4(vertex_ModelSpace, 1);
	
	// Position of the vertex, in worldspace : M * position
	vertex_WorldSpace = (modelMatrix * vec4(vertex_ModelSpace, 1)).xyz;
	
	// Vector that goes from the vertex to the camera, in camera space.
	// In camera space, the camera is at the origin (0,0,0).
	vec3 vertex_CameraSpace = (viewMatrix * modelMatrix * vec4(vertex_ModelSpace, 1)).xyz;
	eyeDir_CameraSpace = vec3(0, 0, 0) - vertex_CameraSpace;

	// Vector that goes from the vertex to the light, in camera space. M is ommited because it's identity.
	vec3 lightPos_CameraSpace = (viewMatrix * vec4(lightPos_WorldSpace, 1)).xyz;
	lightDir_CameraSpace = lightPos_CameraSpace + eyeDir_CameraSpace;
	
	// Normal of the the vertex, in camera space
	normal_CameraSpace = (viewMatrix * modelMatrix * vec4(normal_ModelSpace, 0)).xyz; // Only correct if ModelMatrix does not scale the model ! Use its inverse transpose if not.
	
	// UV of the vertex. No special space for this one.
	texCoords = vertex_TexCoords;
}

// vim:set syntax=glsl:

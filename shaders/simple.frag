#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform vec3 objectColor;
uniform vec3 cameraPosition;

out vec4 color;

void main()
{
    color = vec4(objectColor, 1);
}
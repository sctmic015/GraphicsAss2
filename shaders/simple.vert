#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexTexCoord;
layout (location=2) in vec3 vertexNormal;
layout (location = 3) in vec3 aTangent;
layout (location = 4) in vec3 aBitangent;

//out VS_OUT {
//    vec3 FragPos;
//    vec2 TexCoords;
//    vec3 TangentLightPos;
//    vec3 TangentViewPos;
//    vec3 TangentFragPos;
//} vs_out;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 fragmentTexCoord;
out vec3 fragmentPosition;
out mat3 TBN;

void main()
{
    gl_Position = projection * view * model * vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
    fragmentPosition = (model * vec4(vertexPos,1.0)).xyz;
    vec3 T = normalize(vec3(model * vec4(aTangent,   0.0)));
    vec3 B = normalize(vec3(model * vec4(aBitangent, 0.0)));
    vec3 N = normalize(vec3(model * vec4(vertexNormal,    0.0)));
    TBN = mat3(T, B, N);

    //fragmentNormal = mat3(transpose(inverse(model))) * vertexNormal;
}
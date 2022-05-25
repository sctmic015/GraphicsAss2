#version 330 core

struct PointLight {
    vec3 position;
    vec3 color;
    float strength;
};

in vec2 fragmentTexCoord;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

uniform sampler2D imageTexture;
uniform PointLight Light1;
uniform PointLight Light2;
uniform vec3 cameraPosition;

out vec4 color;

//vec3 calculatePointLight(PointLight light, vec3 fragPosition, vec3 fragNormal);

void main()
{
    vec3 temp = vec3(0);

    vec3 baseTexture = texture(imageTexture, fragmentTexCoord).rgb;
    vec3 resultL1 = vec3(0);

    vec3 positionL1 = Light1.position;
    float strengthL1 = Light1.strength;
    vec3 colorL1 = Light1.color;

    vec3 positionL2 = Light2.position;
    float strengthL2 = Light2.strength;
    vec3 colorL2 = Light2.color;

    vec3 fragToCamera = cameraPosition - fragmentPosition;
    fragToCamera = normalize(fragToCamera);
    vec3 norm = normalize(fragmentNormal);
    vec3 amb = 0.5 * baseTexture;

    // Light 1
    vec3 light1Result = vec3(0);
    vec3 fragToLight1 = positionL1 - fragmentPosition;
    fragToLight1 = normalize(fragToLight1);
    vec3 reflectDir = -reflect(-fragToLight1, norm);
    float kd = max(dot(fragToLight1,fragmentNormal), 0.0);
    float ks = pow(max(dot(fragToCamera,reflectDir),0.0), 32);

    vec3 diffuse1 = colorL1 * strengthL1 * kd/10;
    vec3 specular1 = colorL1 * strengthL1 * ks / 10;
    light1Result = diffuse1 + specular1;

    //Light 2
    vec3 light2Result = vec3(0);
    vec3 fragToLight2 = positionL2 - fragmentPosition;
    fragToLight2 = normalize(fragToLight2);
    vec3 reflectDir2 = -reflect(-fragToLight2, norm);
    float kd2 = max(dot(fragToLight2,fragmentNormal), 0.0);
    float ks2 = pow(max(dot(fragToCamera,reflectDir2),0.0), 32);

    vec3 diffuse2 = colorL2 * strengthL2 * kd2/10;
    vec3 specular2 = colorL2 * strengthL2 * ks2 / 10;
    light2Result = diffuse2 + specular2;

    temp += amb + light1Result + light2Result;

    color = vec4(temp, 1);
}

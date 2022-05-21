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

    vec3 positionL1 = Light1.position;
    float strengthL1 = Light1.strength;
    vec3 colorL1 = Light1.color;

    vec3 positionL2 = Light2.position;
    float strengthL2 = Light2.strength;
    vec3 colorL2 = Light2.color;

    vec3 fragToLight1 = positionL1 - fragmentPosition;
    fragToLight1 = normalize(fragToLight1);
    vec3 fragToCamera = cameraPosition - fragmentPosition;
    fragToCamera = normalize(fragToCamera);
    vec3 halfwayVec = fragToLight1 - fragToCamera;
    halfwayVec = normalize(halfwayVec);

    float kd = max(dot(fragToLight1,fragmentNormal), 0.0);
    float ks = pow(max(dot(fragmentNormal,halfwayVec),0.0), 32);

    vec3 fragToLight2 = positionL2 - fragmentPosition;
    fragToLight2 = normalize(fragToLight2);
    vec3 halfwayVec2 = fragToLight2 - fragToCamera;
    halfwayVec2 = normalize(halfwayVec2);

    float kd2 = max(dot(fragToLight2,fragmentNormal), 0.0);
    float ks2 = pow(max(dot(fragmentNormal,halfwayVec2),0.0), 32);

    vec3 amb = 0.5 * baseTexture;

    vec3 diffuse = colorL1 * strengthL1 * kd;

    vec3 diffuse2 = colorL2 * strengthL2 * kd2;

    vec3 specular = vec3(0, 0, 1) * strengthL1 * ks / 100;

    vec3 specular2 = vec3(0, 0, 1) * strengthL2 * ks2 / 100;
    temp += amb + diffuse + specular + diffuse2 + specular2;

    color = vec4(temp, 1);
}

vec3 calculatePointLight(PointLight light, vec3 fragPosition, vec3 fragNormal) {

    vec3 baseTexture = texture(imageTexture, fragmentTexCoord).rgb;
    vec3 result = vec3(0);

    //geometric data
    vec3 fragLight = light.position - fragPosition;
    float distance = length(fragLight);
    fragLight = normalize(fragLight);
    vec3 fragCamera = normalize(cameraPosition - fragPosition);
    vec3 halfVec = normalize(fragLight - fragCamera);

    //ambient
    result += 0.2 * baseTexture;

    //diffuse
    result += light.color * light.strength * max(0.0, dot(fragNormal, fragLight)) / (distance * distance) * baseTexture;

    //specular
    result += vec3(0, 0, 1) * light.strength * pow(max(0.0, dot(fragNormal, halfVec)),32) / (distance * distance);

    return result;
}
/*
 * OpenGL fragment shader used by fsl/fslview/gl/gl21/glvolume_funcs.py.
 *
 * Author: Paul McCarthy <pauldmccarthy@gmail.com>
 */
#version 120

#pragma include spline_interp.glsl
#pragma include test_in_bounds.glsl

/*
 * image data texture
 */
uniform sampler3D imageTexture;

/*
 * Texture containing the colour map
 */
uniform sampler1D colourTexture;


uniform vec3 imageShape;

/*
 * Use spline interpolation?
 */
uniform bool useSpline;

/*
 * Transformation matrix to apply to the voxel value.
 */
uniform mat4 voxValXform;

/*
 * Clip voxels below this value.
 */
uniform float clipLow;

/*
 * Clip voxels above this value.
 */
uniform float clipHigh;

/*
 * Image voxel coordinates
 */
varying vec3 fragVoxCoord;


void main(void) {

    vec3 voxCoord = fragVoxCoord;

    if (!test_in_bounds(voxCoord, imageShape)) {
        
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }

    /* 
     * Normalise voxel coordinates to (0.0, 1.0)
     */
    vec3 texCoord = voxCoord / imageShape;

    /*
     * Look up the voxel value 
     */
    float voxValue;
    if (useSpline) voxValue = spline_interp(imageTexture,
                                            texCoord,
                                            imageShape,
                                            0);
    else           voxValue = texture3D(    imageTexture,
                                            texCoord).r;

    /*
     * Clip out of range voxel values
     */
    if (voxValue < clipLow || voxValue > clipHigh) {
      
      gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
      return;
    }

    /*
     * Transform the voxel value to a colour map texture
     * coordinate, and look up the colour for the voxel value
     */
    vec4 normVoxValue = voxValXform * vec4(voxValue, 0, 0, 1);
    gl_FragColor      = texture1D(colourTexture, normVoxValue.x);
}

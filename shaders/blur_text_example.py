from PIL import Image
from math import pi, e, sqrt

import arcade
import arcade.gl as gl
import arcade.gl.geometry as geometry

BLUR_COUNT = 1

COMPUTE_SHADER = """

#version 430

layout (local_size_x = 16, local_size_y = 16) in;

layout (rgba8, binding=0) uniform image2D inImage;
layout (rgba8, binding=1) uniform image2D outImage;

const float[9] blurKernel = {1/9, 1/9, 1/9,
                             1/9, 1/9, 1/9,
                             1/9, 1/9, 1/9};

vec4 apply(ivec2 pixelPos){
    ivec2 image_size = imageSize(outImage);
    vec4 total = vec4(0.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-1, -1), 0) * vec4(vec3(blurKernel[0]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(0, -1), 0) * vec4(vec3(blurKernel[1]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(1, -1), 0) * vec4(vec3(blurKernel[2]), 1);
    
    total += texelFetch(inImage, pixelPos+ivec2(-1, 0), 0) * vec4(vec3(blurKernel[3]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(0, 0), 0) * vec4(vec3(blurKernel[4]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(1, 0), 0) * vec4(vec3(blurKernel[5]), 1);
    
    total += texelFetch(inImage, pixelPos+ivec2(-1, 1), 0) * vec4(vec3(blurKernel[6]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(0, 0), 0) * vec4(vec3(blurKernel[7]), 1);
    total += texelFetch(inImage, pixelPos+ivec2(1, 0), 0) * vec4(vec3(blurKernel[8]), 1);
    
    return total;
}


void main(){
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
    
    imageStore(outImage, texelPos, apply(texelPos));
}

"""

VERTEX_SHADER = """
                    #version 330

                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 uv;

                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        uv = in_uv;
                    }
                    """

FRAGMENT_SHADER = """
#version 430

in vec2 uv;
out vec4 fragColor;

layout (binding=0) uniform sampler2D inImage;

const float[81] blurKernel = {1.79105293282802e-08, 5.931152735254126e-07, 7.225623237724327e-06, 3.238299669088985e-05, 5.339053545328196e-05, 3.238299669088985e-05, 7.225623237724327e-06, 5.931152735254126e-07, 1.79105293282802e-08,
                              5.931152735254126e-07, 1.9641280346397447e-05, 0.0002392797792004707, 0.0010723775711956548, 0.001768051711852017, 0.0010723775711956548, 0.0002392797792004707, 1.9641280346397447e-05, 5.931152735254126e-07,
                              7.225623237724327e-06, 0.0002392797792004707, 0.0029150244650281948, 0.013064233284684923, 0.021539279301848634, 0.013064233284684923, 0.0029150244650281948, 0.0002392797792004707, 7.225623237724327e-06,
                              3.238299669088985e-05, 0.0010723775711956548, 0.013064233284684923, 0.05854983152431917, 0.09653235263005391, 0.05854983152431917, 0.013064233284684923, 0.0010723775711956548, 3.238299669088985e-05,
                              5.339053545328196e-05, 0.001768051711852017, 0.021539279301848634, 0.09653235263005391, 0.15915494309189535, 0.09653235263005391, 0.021539279301848634, 0.001768051711852017, 5.339053545328196e-05,
                              3.238299669088985e-05, 0.0010723775711956548, 0.013064233284684923, 0.05854983152431917, 0.09653235263005391, 0.05854983152431917, 0.013064233284684923, 0.0010723775711956548, 3.238299669088985e-05,
                              7.225623237724327e-06, 0.0002392797792004707, 0.0029150244650281948, 0.013064233284684923, 0.021539279301848634, 0.013064233284684923, 0.0029150244650281948, 0.0002392797792004707, 7.225623237724327e-06,
                              5.931152735254126e-07, 1.9641280346397447e-05, 0.0002392797792004707, 0.0010723775711956548, 0.001768051711852017, 0.0010723775711956548, 0.0002392797792004707, 1.9641280346397447e-05, 5.931152735254126e-07,
                              1.79105293282802e-08, 5.931152735254126e-07, 7.225623237724327e-06, 3.238299669088985e-05, 5.339053545328196e-05, 3.238299669088985e-05, 7.225623237724327e-06, 5.931152735254126e-07, 1.79105293282802e-08};

vec4 apply(ivec2 pixelPos){
    vec4 total = vec4(0.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, -4), 0) * vec4(vec3(blurKernel[0]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, -4), 0) * vec4(vec3(blurKernel[1]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, -4), 0) * vec4(vec3(blurKernel[2]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, -4), 0) * vec4(vec3(blurKernel[3]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, -4), 0) * vec4(vec3(blurKernel[4]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, -4), 0) * vec4(vec3(blurKernel[5]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, -4), 0) * vec4(vec3(blurKernel[6]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, -4), 0) * vec4(vec3(blurKernel[7]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, -4), 0) * vec4(vec3(blurKernel[8]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, -3), 0) * vec4(vec3(blurKernel[9]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, -3), 0) * vec4(vec3(blurKernel[10]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, -3), 0) * vec4(vec3(blurKernel[11]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, -3), 0) * vec4(vec3(blurKernel[12]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, -3), 0) * vec4(vec3(blurKernel[13]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, -3), 0) * vec4(vec3(blurKernel[14]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, -3), 0) * vec4(vec3(blurKernel[15]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, -3), 0) * vec4(vec3(blurKernel[16]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, -3), 0) * vec4(vec3(blurKernel[17]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, -2), 0) * vec4(vec3(blurKernel[18]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, -2), 0) * vec4(vec3(blurKernel[19]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, -2), 0) * vec4(vec3(blurKernel[20]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, -2), 0) * vec4(vec3(blurKernel[21]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, -2), 0) * vec4(vec3(blurKernel[22]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, -2), 0) * vec4(vec3(blurKernel[23]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, -2), 0) * vec4(vec3(blurKernel[24]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, -2), 0) * vec4(vec3(blurKernel[25]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, -2), 0) * vec4(vec3(blurKernel[26]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, -1), 0) * vec4(vec3(blurKernel[27]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, -1), 0) * vec4(vec3(blurKernel[28]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, -1), 0) * vec4(vec3(blurKernel[29]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, -1), 0) * vec4(vec3(blurKernel[30]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, -1), 0) * vec4(vec3(blurKernel[31]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, -1), 0) * vec4(vec3(blurKernel[32]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, -1), 0) * vec4(vec3(blurKernel[33]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, -1), 0) * vec4(vec3(blurKernel[34]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, -1), 0) * vec4(vec3(blurKernel[35]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, 0), 0) * vec4(vec3(blurKernel[36]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, 0), 0) * vec4(vec3(blurKernel[37]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, 0), 0) * vec4(vec3(blurKernel[38]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, 0), 0) * vec4(vec3(blurKernel[39]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, 0), 0) * vec4(vec3(blurKernel[40]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, 0), 0) * vec4(vec3(blurKernel[41]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, 0), 0) * vec4(vec3(blurKernel[42]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, 0), 0) * vec4(vec3(blurKernel[43]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, 0), 0) * vec4(vec3(blurKernel[44]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, 1), 0) * vec4(vec3(blurKernel[45]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, 1), 0) * vec4(vec3(blurKernel[46]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, 1), 0) * vec4(vec3(blurKernel[47]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, 1), 0) * vec4(vec3(blurKernel[48]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, 1), 0) * vec4(vec3(blurKernel[49]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, 1), 0) * vec4(vec3(blurKernel[50]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, 1), 0) * vec4(vec3(blurKernel[51]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, 1), 0) * vec4(vec3(blurKernel[52]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, 1), 0) * vec4(vec3(blurKernel[53]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, 2), 0) * vec4(vec3(blurKernel[54]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, 2), 0) * vec4(vec3(blurKernel[55]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, 2), 0) * vec4(vec3(blurKernel[56]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, 2), 0) * vec4(vec3(blurKernel[57]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, 2), 0) * vec4(vec3(blurKernel[58]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, 2), 0) * vec4(vec3(blurKernel[59]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, 2), 0) * vec4(vec3(blurKernel[60]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, 2), 0) * vec4(vec3(blurKernel[61]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, 2), 0) * vec4(vec3(blurKernel[62]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, 3), 0) * vec4(vec3(blurKernel[63]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, 3), 0) * vec4(vec3(blurKernel[64]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, 3), 0) * vec4(vec3(blurKernel[65]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, 3), 0) * vec4(vec3(blurKernel[66]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, 3), 0) * vec4(vec3(blurKernel[67]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, 3), 0) * vec4(vec3(blurKernel[68]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, 3), 0) * vec4(vec3(blurKernel[69]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, 3), 0) * vec4(vec3(blurKernel[70]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, 3), 0) * vec4(vec3(blurKernel[71]), 1.0);
    
    total += texelFetch(inImage, pixelPos+ivec2(-4, 4), 0) * vec4(vec3(blurKernel[72]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-3, 4), 0) * vec4(vec3(blurKernel[73]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-2, 4), 0) * vec4(vec3(blurKernel[74]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(-1, 4), 0) * vec4(vec3(blurKernel[75]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(0, 4), 0) * vec4(vec3(blurKernel[76]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(1, 4), 0) * vec4(vec3(blurKernel[77]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(2, 4), 0) * vec4(vec3(blurKernel[78]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(3, 4), 0) * vec4(vec3(blurKernel[79]), 1.0);
    total += texelFetch(inImage, pixelPos+ivec2(4, 4), 0) * vec4(vec3(blurKernel[80]), 1.0);
    
    return total*3;
}

void main(){
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_FragCoord.xy);
    
    fragColor = apply(texelPos);
}

"""


class BlurryTextExample(arcade.Window):

    def __init__(self):
        super().__init__(400, 400, "glowing text", gl_version=(4, 3))
        self.text = arcade.Text("EXAMPLE TEXT", 0, 0, arcade.color.RED, anchor_x='center', anchor_y='center')
        text_size = self.text.content_size

        # Each work group is 16x16 find how many there needs to be for at least 1 to go out on each side.
        self.work_group_count = text_size[0]//16 + 3, text_size[1]//16 + 3
        self.image_size = self.work_group_count[0]*16, self.work_group_count[1]*16

        # Place the image roughly in the center
        self.text.x = self.image_size[0]//2
        self.text.y = self.image_size[1]//2

        self.render_quad = geometry.quad_2d_fs()
        self.blur_program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
        # The two images we will bounce between to do the blurring.
        self.image_1 = self.ctx.texture(self.image_size, components=4, wrap_x=gl.CLAMP_TO_EDGE, wrap_y=gl.CLAMP_TO_EDGE,
                                        filter=(gl.NEAREST, gl.NEAREST))
        self.image_2 = self.ctx.texture(self.image_size, components=4, wrap_x=gl.CLAMP_TO_EDGE, wrap_y=gl.CLAMP_TO_EDGE,
                                        filter=(gl.NEAREST, gl.NEAREST))

        # We have to draw the text onto the framebuffer so that image_1 will have the text in it. If we did not do this
        # step we would have no way of blurring the text!
        framebuffer_1 = self.ctx.framebuffer(color_attachments=self.image_1)
        framebuffer_2 = self.ctx.framebuffer(color_attachments=self.image_2)

        self.ctx.disable(self.ctx.BLEND)

        framebuffer_1.use()
        framebuffer_1.clear()
        # Since we have text which uses a projection matrix we have to change the viewport
        arcade.set_viewport(0, self.image_size[0], 0, self.image_size[1])
        self.text.draw()

        framebuffer_2.use()
        framebuffer_2.clear()

        self.image_1.use(0)

        self.render_quad.render(self.blur_program)

        self.text.color = arcade.color.WHITE
        self.text.draw()

        self.use()
        arcade.set_viewport(0, self.width, 0, self.height)

        # Visualize the texture
        self.program = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader="""
                    #version 330

                    uniform sampler2D image;
                    in vec2 uv;
                    out vec4 fragColor;

                    void main() {
                        fragColor = texture(image, uv);
                    }
                    """,
        )
        self.quad = geometry.quad_2d(size=(2, 1))

    def on_draw(self):
        self.clear()
        # self.text.draw()

        self.image_2.use(0)
        self.quad.render(self.program)


def main():
    test = [(1/(sqrt(2*pi)))*pow(e, -(x**2/2)) for x in range(-4, 5)]
    final = [test[x]*test[y] for y in range(0, 9) for x in range(0, 9)]
    window = BlurryTextExample()
    window.run()


if __name__ == '__main__':
    main()

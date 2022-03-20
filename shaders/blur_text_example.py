from PIL import Image

import arcade
import arcade.gl as gl
import arcade.gl.geometry as geometry

BLUR_COUNT = 1

COMPUTE_SHADER = """

#version 430

layout (local_size_x = 16, local_size_y = 16) in;

layout (rgba8, location=1) uniform image2D inImage;
layout (rgba8, location=0) uniform image2D outImage;

const float[9] blurKernel = {1/9, 1/9, 1/9,
                             1/9, 1/9, 1/9,
                             1/9, 1/9, 1/9};

vec4 apply(ivec2 pixelPos){
    ivec2 image_size = imageSize(inImage);
    vec4 total = vec4(0.0);
    
    total += imageLoad(inImage, clamp(pixelPos+ivec2(-1, -1), ivec2(0, 0), image_size)) * blurKernel[0];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(0, -1), ivec2(0, 0), image_size)) * blurKernel[1];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(1, -1), ivec2(0, 0), image_size)) * blurKernel[2];
    
    total += imageLoad(inImage, clamp(pixelPos+ivec2(-1, 0), ivec2(0, 0), image_size)) * blurKernel[3];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(0, 0), ivec2(0, 0), image_size)) * blurKernel[4];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(1, 0), ivec2(0, 0), image_size)) * blurKernel[5];
    
    total += imageLoad(inImage, clamp(pixelPos+ivec2(-1, 1), ivec2(0, 0), image_size)) * blurKernel[6];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(0, 0), ivec2(0, 0), image_size)) * blurKernel[7];
    total += imageLoad(inImage, clamp(pixelPos+ivec2(1, 0), ivec2(0, 0), image_size)) * blurKernel[8];
    
    return total;
}


void main(){
    // texel coordinate we are writing to
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
    
    imageStore(outImage, texelPos, apply(texelPos));
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

        # The two images we will bounce between to do the blurring.
        self.image_1 = self.ctx.texture(self.image_size, components=4,
                                        filter=(gl.NEAREST, gl.NEAREST))
        self.image_2 = self.ctx.texture(self.image_size, components=4,
                                        filter=(gl.NEAREST, gl.NEAREST))

        # We have to draw the text onto the framebuffer so that image_1 will have the text in it. If we did not do this
        # step we would have no way of blurring the text!
        framebuffer = self.ctx.framebuffer(color_attachments=self.image_1)
        framebuffer.use()
        framebuffer.clear()
        # Since we have text which uses a projection matrix we have to change the viewport
        arcade.set_viewport(0, self.image_size[0], 0, self.image_size[1])
        self.text.draw()
        self.use()
        arcade.set_viewport(0, self.width, 0, self.height)

        self.blurShader = self.ctx.compute_shader(source=COMPUTE_SHADER)
        self.ctx.disable(self.ctx.BLEND)

        self.image_1.bind_to_image(1, read=True)
        self.image_2.bind_to_image(0, write=True)

        self.blurShader.run(group_x=self.work_group_count[0], group_y=self.work_group_count[1], group_z=1)
        print(self.image_2.read())
        self.image_2, self.image_1 = self.image_1, self.image_2

        framebuffer = self.ctx.framebuffer(color_attachments=self.image_1)
        self.text.color = arcade.color.WHITE
        framebuffer.use()
        # Since we have text which uses a projection matrix we have to change the viewport
        arcade.set_viewport(0, self.image_size[0], 0, self.image_size[1])
        self.text.draw()
        self.use()
        arcade.set_viewport(0, self.width, 0, self.height)

        # Visualize the texture
        self.program = self.ctx.program(
            vertex_shader="""
                    #version 330

                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 uv;

                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        uv = in_uv;
                    }
                    """,
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

        self.image_1.use(0)
        self.quad.render(self.program)


def main():
    window = BlurryTextExample()
    window.run()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Offscreen integration checks using the real baseline shaders on macOS.

Emulates documented loader MRT routing, alpha testing, and ping-pong manually.
Minecraft draw dispatch and Iris shader rewriting still need in-game testing.
"""
import ctypes as C
from validate import Driver, preprocess, SHADERS


def main():
    driver = Driver()
    gl = driver.gl
    U, I, F, D = C.c_uint, C.c_int, C.c_float, C.c_double
    for name, result, args in [
        ('glGenTextures', None, [I, C.POINTER(U)]),
        ('glBindTexture', None, [U, U]),
        ('glTexImage2D', None, [U, I, I, I, I, I, U, U, C.c_void_p]),
        ('glTexParameteri', None, [U, U, I]),
        ('glActiveTexture', None, [U]),
        ('glGenFramebuffersEXT', None, [I, C.POINTER(U)]),
        ('glBindFramebufferEXT', None, [U, U]),
        ('glFramebufferTexture2DEXT', None, [U, U, U, U, I]),
        ('glCheckFramebufferStatusEXT', U, [U]),
        ('glDrawBuffers', None, [I, C.POINTER(U)]),
        ('glReadBuffer', None, [U]),
        ('glReadPixels', None, [I, I, I, I, U, U, C.c_void_p]),
        ('glViewport', None, [I, I, I, I]),
        ('glClearColor', None, [F, F, F, F]),
        ('glClear', None, [U]),
        ('glUseProgram', None, [U]),
        ('glGetUniformLocation', I, [U, C.c_char_p]),
        ('glUniform1i', None, [I, I]),
        ('glEnable', None, [U]),
        ('glDisable', None, [U]),
        ('glDisableIndexedEXT', None, [U, U]),
        ('glAlphaFunc', None, [U, F]),
        ('glBlendFuncSeparate', None, [U, U, U, U]),
        ('glBegin', None, [U]),
        ('glEnd', None, []),
        ('glVertex3f', None, [F, F, F]),
        ('glColor4f', None, [F, F, F, F]),
        ('glNormal3f', None, [F, F, F]),
        ('glTexCoord2f', None, [F, F]),
        ('glMultiTexCoord2f', None, [U, F, F]),
        ('glVertexAttrib3f', None, [U, F, F, F]),
    ]:
        driver.bind(name, result, *args)

    programs = {}
    def use(name):
        if name not in programs:
            programs[name] = driver.program(preprocess(SHADERS / (name + '.vsh')),
                                            preprocess(SHADERS / (name + '.fsh')))
        program = programs[name]
        gl.glUseProgram(program)
        for uniform, unit in [('gtexture', 0), ('lightmap', 1), ('colortex0', 0)]:
            loc = gl.glGetUniformLocation(program, uniform.encode())
            if loc >= 0:
                gl.glUniform1i(loc, unit)

    def texture(fmt, width=4, pixel=None):
        result = U()
        gl.glGenTextures(1, C.byref(result))
        gl.glBindTexture(0x0DE1, result)
        gl.glTexParameteri(0x0DE1, 0x2801, 0x2600)  # nearest
        gl.glTexParameteri(0x0DE1, 0x2800, 0x2600)
        gl.glTexParameteri(0x0DE1, 0x2802, 0x812F)  # clamp to edge
        gl.glTexParameteri(0x0DE1, 0x2803, 0x812F)
        data = (F * 4)(*pixel) if pixel else None
        gl.glTexImage2D(0x0DE1, 0, fmt, width, width, 0, 0x1908, 0x1406, data)
        return result.value

    fbo = U()
    gl.glGenFramebuffersEXT(1, C.byref(fbo))
    gl.glBindFramebufferEXT(0x8D40, fbo)
    targets = [texture(fmt) for fmt in [0x8058, 0x8058, 0x881A, 0x8814]]
    alternate = texture(0x8058)
    presented = texture(0x8058)
    source = texture(0x8058, 1, (0.8, 0.4, 0.2, 0.5))
    light = texture(0x8058, 1, (0.5, 0.25, 1.0, 1.0))

    def attach(ids):
        for i in range(4):
            gl.glFramebufferTexture2DEXT(0x8D40, 0x8CE0+i, 0x0DE1, ids[i] if i < len(ids) else 0, 0)
        gl.glDrawBuffers(len(ids), (U * len(ids))(*(0x8CE0+i for i in range(len(ids)))))
        gl.glReadBuffer(0x8CE0)
        assert gl.glCheckFramebufferStatusEXT(0x8D40) == 0x8CD5, 'Incomplete framebuffer'

    def bind(unit, tex):
        gl.glActiveTexture(0x84C0 + unit)
        gl.glBindTexture(0x0DE1, tex)

    def draw(color=(1, 1, 1, 1)):
        gl.glColor4f(*color)
        gl.glNormal3f(0, 0, 1)
        gl.glVertexAttrib3f(10, 4, 0, 0)
        gl.glMultiTexCoord2f(0x84C1, 0.5, 0.5)
        gl.glBegin(5)  # triangle strip
        for x, y in [(0,0), (1,0), (0,1), (1,1)]:
            gl.glTexCoord2f(x, y)
            gl.glVertex3f(x*2-1, y*2-1, 0)
        gl.glEnd()

    def pixel(index=0):
        gl.glReadBuffer(0x8CE0 + index)
        result = (F * 4)()
        gl.glReadPixels(2, 2, 1, 1, 0x1908, 0x1406, result)
        return list(result)

    def check(actual, expected, label, tolerance=0.009):
        assert all(abs(a-b) < tolerance for a,b in zip(actual, expected)), (label, actual, expected)
        assert gl.glGetError() == 0, label + ': OpenGL error'
        print('PASS:', label)

    try:
        attach(targets)
        gl.glViewport(0, 0, 4, 4)
        gl.glDisable(0x0B71)  # depth (no depth attachment in this test)
        gl.glDisable(0x0BE2)  # blending
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(0x4000)
        bind(0, source)
        bind(1, light)
        use('gbuffers_terrain')
        gl.glEnable(0x0BC0)
        gl.glAlphaFunc(0x0204, 0.1)  # loader alpha test, GREATER
        draw((0.5, 1, 0.5, 0.5))
        original = pixel()
        check(original, [0.2, 0.1, 0.1, 0.25], 'texture × vertex tint × lightmap; alpha preserved')
        check(pixel(1), [0.4, 0.4, 0.1, 0.25], 'unlit surface and coverage')
        check(pixel(2), [0.5, 0.5, 1, 1], 'normal and validity')
        check(pixel(3), [0.5, 0.5, 4, 1], 'light UV, material ID, geometry family')
        draw((1, 1, 1, 0))
        check(pixel(), original, 'cutout rejects invisible texels')
        check(pixel(3), [0.5, 0.5, 4, 1], 'cutout does not overwrite metadata')
        gl.glDisable(0x0BC0)

        attach([alternate])
        bind(0, targets[0])
        use('deferred')
        draw()
        check(pixel(), original, 'deferred ping-pong identity')

        # Apply the per-buffer blend policy from shaders.properties.
        attach([alternate, targets[1], targets[2], targets[3]])
        bind(0, source)
        bind(1, light)
        use('gbuffers_water')
        gl.glEnable(0x0BE2)
        for index in (1, 2, 3):
            gl.glDisableIndexedEXT(0x0BE2, index)
        gl.glBlendFuncSeparate(0x0302, 0x0303, 1, 0x0303)
        draw()
        blended = pixel()
        check(blended, [0.3, 0.1, 0.15, 0.625], 'translucency blends onto deferred result')
        check(pixel(1), [0.8, 0.4, 0.2, 0.5], 'translucent metadata stays unblended')
        check(pixel(3), [0.5, 0.5, 4, 5], 'translucent material identity stays intact')
        gl.glDisable(0x0BE2)

        attach([targets[0]])
        bind(0, alternate)
        use('composite')
        draw()
        check(pixel(), blended, 'composite preserves scene including translucency')
        attach([presented])
        bind(0, targets[0])
        use('final')
        draw()
        check(pixel(), blended, 'final preserves scene color and alpha')

        use('gbuffers_skybasic')
        draw((0.2, 0.3, 0.8, 1))
        check(pixel(), [0.2, 0.3, 0.8, 1], 'untextured sky stays visible')
        use('gbuffers_weather')
        bind(0, source)
        bind(1, light)
        draw()
        check(pixel(), [0.4, 0.1, 0.2, 0.5], 'weather texture and lightmap stay visible')
        print('All offscreen checks passed. Minecraft validation is still required.')
    finally:
        for program in programs.values():
            gl.glDeleteProgram(program)
        driver.close()


if __name__ == '__main__':
    main()

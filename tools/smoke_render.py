#!/usr/bin/env python3
"""Offscreen integration checks using the real baseline shaders on macOS.

Emulates documented loader MRT routing, alpha testing, and ping-pong manually.
Minecraft draw dispatch and Iris shader rewriting still need in-game testing.
"""
import ctypes as C
import math
import sys
from pathlib import Path
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
        ('glUniform1f', None, [I, F]),
        ('glUniform3f', None, [I, F, F, F]),
        ('glUniformMatrix4fv', None, [I, I, U, C.POINTER(F)]),
        ('glTexSubImage2D', None, [U, I, I, I, I, I, U, U, C.c_void_p]),
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
        ('glMatrixMode', None, [U]),
        ('glLoadMatrixf', None, [C.POINTER(F)]),
        ('glDepthFunc', None, [U]),
    ]:
        driver.bind(name, result, *args)

    programs = {}
    def use(name, effects=None):
        options = dict(BLOHO_BLOOM=0, BLOHO_FOG=0, BLOHO_CLOUDS=0,
                       BLOHO_LIGHTING=0, BLOHO_SHADOWS=0, BLOHO_GRADE=0, BLOHO_WATER=0)
        options.update(effects or {})
        key = (name, tuple(sorted(options.items())))
        if key not in programs:
            programs[key] = driver.program(preprocess(SHADERS / (name + '.vsh'), options),
                                            preprocess(SHADERS / (name + '.fsh'), options))
        program = programs[key]
        gl.glUseProgram(program)
        for uniform, unit in [('gtexture', 0), ('lightmap', 1), ('colortex0', 0),
                              ('colortex4', 2), ('colortex5', 3), ('depthtex0', 4), ('shadowtex0', 5)]:
            loc = gl.glGetUniformLocation(program, uniform.encode())
            if loc >= 0:
                gl.glUniform1i(loc, unit)
        return program

    def uniform(program, name, *values):
        location = gl.glGetUniformLocation(program, name.encode())
        if len(values) == 3:
            gl.glUniform3f(location, *values)
        elif isinstance(values[0], int):
            gl.glUniform1i(location, values[0])
        else:
            gl.glUniform1f(location, values[0])

    def matrix(program, name, values):
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(program, name.encode()), 1, 0, (F * 16)(*values))

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

    def draw(color=(1, 1, 1, 1), z=0, material=4):
        gl.glColor4f(*color)
        gl.glNormal3f(0, 0, 1)
        gl.glVertexAttrib3f(10, material, 0, 0)
        gl.glMultiTexCoord2f(0x84C1, 0.5, 0.5)
        gl.glBegin(5)  # triangle strip
        for x, y in [(0,0), (1,0), (0,1), (1,1)]:
            gl.glTexCoord2f(x, y)
            gl.glVertex3f(x*2-1, y*2-1, z)
        gl.glEnd()

    def pixel(index=0, x=2, y=2):
        gl.glReadBuffer(0x8CE0 + index)
        result = (F * 4)()
        gl.glReadPixels(x, y, 1, 1, 0x1908, 0x1406, result)
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

        # Fog must affect scene RGB without affecting alpha or the raw metadata.
        attach(targets)
        program = use('gbuffers_terrain', {'BLOHO_FOG': 1})
        uniform(program, 'fogMode', 9729)
        uniform(program, 'fogStart', 0.0)
        uniform(program, 'fogEnd', 0.2)
        uniform(program, 'fogColor', 0.1, 0.3, 0.6)
        draw()
        check(pixel(), [0.1, 0.3, 0.6, 0.5], 'linear fog reaches engine fog color without changing alpha')
        check(pixel(1), [0.8, 0.4, 0.2, 0.5], 'fog leaves surface metadata unchanged')
        uniform(program, 'fogMode', 2048)
        uniform(program, 'fogDensity', 2.0)
        draw()
        visibility = math.exp(-2.0 * math.sqrt(0.25**2 + 0.25**2))
        expected = [f + (c-f)*visibility for c,f in zip([0.4, 0.1, 0.2], [0.1, 0.3, 0.6])] + [0.5]
        check(pixel(), expected, 'exponential fog uses per-fragment distance')
        uniform(program, 'fogMode', 2049)
        draw()
        visibility = math.exp(-0.5)
        expected = [f + (c-f)*visibility for c,f in zip([0.4, 0.1, 0.2], [0.1, 0.3, 0.6])] + [0.5]
        check(pixel(), expected, 'exponential-squared fog')
        attach([presented])
        program = use('gbuffers_spidereyes', {'BLOHO_FOG': 1})
        uniform(program, 'fogMode', 9729)
        uniform(program, 'fogStart', 0.0)
        uniform(program, 'fogEnd', 0.2)
        uniform(program, 'fogColor', 0.1, 0.3, 0.6)
        draw()
        check(pixel(), [0, 0, 0, 0.5], 'additive eyes fade to black rather than add fog color')

        # Bloom test: a small bright square in a black 32x32 input, half-res blur.
        bind(0, 0)
        scene = texture(0x8058, 32)
        zero = (F * (32*32*4))()
        gl.glTexSubImage2D(0x0DE1, 0, 0, 0, 32, 32, 0x1908, 0x1406, zero)
        bright = (F * 64)(*([1, 0.9, 0.7, 0.4] * 16))
        gl.glTexSubImage2D(0x0DE1, 0, 14, 14, 4, 4, 0x1908, 0x1406, bright)
        bloomA, bloomB = texture(0x881A, 16), texture(0x881A, 16)
        for name, target, inputUnit, inputTex in [('composite1', bloomA, 0, scene),
                                                  ('composite2', bloomB, 2, bloomA),
                                                  ('composite3', bloomA, 3, bloomB)]:
            attach([target])
            gl.glViewport(0, 0, 16, 16)
            bind(inputUnit, inputTex)
            program = use(name, {'BLOHO_BLOOM': 1})
            uniform(program, 'viewWidth', 32.0)
            uniform(program, 'viewHeight', 32.0)
            draw()
        bloomNear = pixel(x=5, y=7)
        assert bloomNear[0] > 0.001, bloomNear
        check(pixel(x=7, y=5), bloomNear, 'bloom spreads symmetrically in both axes', 0.015)
        assert pixel(x=8, y=8)[0] < 1.0, 'Bloom kernel must not amplify a unit impulse'
        print('PASS: bloom spreads energy away from small highlights')
        attach([presented])
        gl.glViewport(0, 0, 4, 4)
        bind(0, source)
        bind(2, bloomA)
        use('final', {'BLOHO_BLOOM': 1})
        draw()
        finalPixel = pixel()
        assert finalPixel[0] >= 0.8 and finalPixel[0] <= 1.0, finalPixel
        check(finalPixel[3:], [0.5], 'bloom resolve preserves scene alpha')
        # Uniform low-valued input must not produce a bloom veil.
        attach([bloomA])
        gl.glViewport(0, 0, 16, 16)
        bind(0, light)
        # Light's blue is 1: use an explicitly dim neutral input instead.
        dim = texture(0x8058, 1, (0.2, 0.2, 0.2, 1))
        bind(0, dim)
        program = use('composite1', {'BLOHO_BLOOM': 1})
        uniform(program, 'viewWidth', 32.0)
        uniform(program, 'viewHeight', 32.0)
        draw()
        check(pixel(), [0, 0, 0, 1], 'dim scenes produce no bloom')

        # Cloud tests use a controlled camera looking up at the two cloud sheets.
        attach([presented])
        gl.glViewport(0, 0, 4, 4)
        bind(4, 0)
        skyDepth = texture(0x8058, 1, (1, 1, 1, 1))
        nearDepth = texture(0x8058, 1, (0.8, 0.8, 0.8, 1))
        bind(0, dim)
        bind(4, skyDepth)
        program = use('deferred', {'BLOHO_CLOUDS': 1, 'CLOUD_COVERAGE': 0.7})
        identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        # Rotate view +Z to world +Y, without a singular matrix.
        up = [1,0,0,0, 0,0,-1,0, 0,1,0,0, 0,0,0,1]
        matrix(program, 'gbufferProjectionInverse', identity)
        matrix(program, 'gbufferModelViewInverse', up)
        uniform(program, 'sunPosition', 0.0, 0.0, 100.0)
        uniform(program, 'skyColor', 0.2, 0.4, 0.7)
        uniform(program, 'fogColor', 0.4, 0.5, 0.6)
        # Scan several camera positions: cloud holes are intentional.
        cloudSeen = False
        for position in range(8):
            uniform(program, 'cameraPosition', float(position * 80), 64.0, 0.0)
            draw()
            if pixel()[0] > 0.21:
                cloudSeen = True
                break
        assert cloudSeen, 'Procedural clouds never become visible'
        print('PASS: procedural clouds are visible against sky')
        bind(4, nearDepth)
        draw()
        check(pixel(), [0.2, 0.2, 0.2, 1], 'near geometry occludes procedural clouds')
        bind(4, skyDepth)
        uniform(program, 'isEyeInWater', 1)
        draw()
        check(pixel(), [0.2, 0.2, 0.2, 1], 'clouds bypass fluid views')
        use('world-1/deferred', {'BLOHO_CLOUDS': 1})
        draw()
        check(pixel(), [0.2, 0.2, 0.2, 1], 'Nether bypasses procedural clouds')
        use('world1/deferred', {'BLOHO_CLOUDS': 1})
        draw()
        check(pixel(), [0.2, 0.2, 0.2, 1], 'End bypasses procedural clouds')

        # v0.3: cast a real depth shadow, then sample it in surface lighting.
        bind(5, 0)
        shadowDepth = U()
        gl.glGenTextures(1, C.byref(shadowDepth))
        gl.glBindTexture(0x0DE1, shadowDepth)
        gl.glTexParameteri(0x0DE1, 0x2801, 0x2600)
        gl.glTexParameteri(0x0DE1, 0x2800, 0x2600)
        gl.glTexImage2D(0x0DE1, 0, 0x81A6, 4, 4, 0, 0x1902, 0x1406, None)
        attach([presented])
        gl.glFramebufferTexture2DEXT(0x8D40, 0x8D00, 0x0DE1, shadowDepth.value, 0)
        assert gl.glCheckFramebufferStatusEXT(0x8D40) == 0x8CD5
        gl.glEnable(0x0B71)
        gl.glDepthFunc(0x0201)
        gl.glClear(0x0100)
        inverseZ = [1,0,0,0, 0,1,0,0, 0,0,-1,0, 0,0,0,1]
        gl.glMatrixMode(0x1701)
        gl.glLoadMatrixf((F * 16)(*inverseZ))
        bind(0, dim)
        use('shadow')
        draw(z=0.5, material=-1)
        depthPixel = (F * 1)()
        gl.glReadPixels(2, 2, 1, 1, 0x1902, 0x1406, depthPixel)
        check(list(depthPixel), [0.25], 'shadow caster writes light-camera depth')
        gl.glClear(0x0100)
        draw((1, 1, 1, 0), z=0.5, material=-1)
        gl.glReadPixels(2, 2, 1, 1, 0x1902, 0x1406, depthPixel)
        check(list(depthPixel), [1.0], 'shadow cutouts preserve depth holes')
        draw(z=0.5, material=1)
        gl.glReadPixels(2, 2, 1, 1, 0x1902, 0x1406, depthPixel)
        check(list(depthPixel), [1.0], 'water does not cast an opaque shadow')
        draw(z=0.5, material=-1)
        gl.glFramebufferTexture2DEXT(0x8D40, 0x8D00, 0x0DE1, 0, 0)
        gl.glDisable(0x0B71)
        gl.glLoadMatrixf((F * 16)(*identity))
        gl.glMatrixMode(0x1700)
        bind(0, dim)
        bind(1, 0)
        fullLight = texture(0x8058, 1, (1, 1, 1, 1))
        bind(1, fullLight)
        bind(5, shadowDepth.value)

        def setLighting(program):
            matrix(program, 'gbufferModelViewInverse', identity)
            matrix(program, 'gbufferModelView', identity)
            matrix(program, 'shadowModelView', identity)
            matrix(program, 'shadowProjection', inverseZ)
            uniform(program, 'sunPosition', 0.0, 100.0, 100.0)
            uniform(program, 'shadowLightPosition', 0.0, 0.0, 100.0)

        program = use('gbuffers_terrain', {'BLOHO_LIGHTING': 1, 'BLOHO_SHADOWS': 1})
        setLighting(program)
        draw(material=-1)
        inShadow = pixel()
        program = use('gbuffers_terrain', {'BLOHO_LIGHTING': 1, 'BLOHO_SHADOWS': 0})
        setLighting(program)
        draw(material=-1)
        inSun = pixel()
        assert inSun[0] > inShadow[0] + 0.02, (inSun, inShadow)
        assert min(inShadow[:3]) > 0.0, 'Shadow must retain ambient light'
        check(inSun[3:], inShadow[3:], 'shadows change illumination without changing alpha')
        print('PASS: actual shadow depth darkens the receiver while retaining ambient')

        # Confirm the promoted scene attachment retains emission above 1.0.
        bind(0, 0)
        hdrTarget = texture(0x881A, 4)
        brightSurface = texture(0x8058, 1, (0.9, 0.7, 0.4, 0.65))
        attach([hdrTarget])
        bind(0, brightSurface)
        program = use('gbuffers_terrain', {'BLOHO_LIGHTING': 1})
        setLighting(program)
        draw(material=5)
        hdrPixel = pixel()
        assert hdrPixel[0] > 1.5, hdrPixel
        check(hdrPixel[3:], [0.65], 'emissive HDR scene preserves alpha')
        print('PASS: emissive highlights survive above display white')
        attach([presented])
        bind(0, hdrTarget)
        use('final', {'BLOHO_GRADE': 1})
        draw()
        graded = pixel()
        assert 0.0 < graded[2] < graded[1] < graded[0] < 1.0, graded
        check(graded[3:], [0.65], 'highlight roll-off preserves hue order and alpha')
        # Contrast is anchored at black; no accidental haze from the grade.
        bind(0, 0)
        black = texture(0x8058, 1, (0, 0, 0, 0.35))
        use('final', {'BLOHO_GRADE': 1})
        draw()
        check(pixel(), [0, 0, 0, 0.35], 'color grade preserves black and alpha')
        # Water normal/sheen path is finite and keeps texture opacity intact.
        bind(0, brightSurface)
        program = use('gbuffers_water', {'BLOHO_LIGHTING': 1, 'BLOHO_WATER': 1})
        setLighting(program)
        uniform(program, 'skyColor', 0.25, 0.45, 0.8)
        draw(material=1)
        waterPixel = pixel()
        assert all(math.isfinite(x) for x in waterPixel), waterPixel
        check(waterPixel[3:], [0.65], 'animated water lighting preserves opacity')

        if '--preview' in sys.argv:
            bind(0, 0)
            previewTarget = texture(0x8058, 512)
            backdrop = texture(0x8058, 1, (0.33, 0.55, 0.81, 1))
            attach([previewTarget])
            gl.glViewport(0, 0, 512, 512)
            bind(0, backdrop)
            bind(4, skyDepth)
            program = use('deferred', {'BLOHO_CLOUDS': 1})
            matrix(program, 'gbufferProjectionInverse', identity)
            s, c = 0.55, math.sqrt(1.0 - 0.55**2)
            matrix(program, 'gbufferModelViewInverse', [1,0,0,0, 0,c,-s,0, 0,s,c,0, 0,0,0,1])
            uniform(program, 'sunPosition', 0.0, 0.0, 100.0)
            uniform(program, 'skyColor', 0.33, 0.55, 0.81)
            uniform(program, 'fogColor', 0.6, 0.7, 0.81)
            uniform(program, 'cameraPosition', 0.0, 64.0, 0.0)
            draw()
            data = (C.c_ubyte * (512 * 512 * 3))()
            gl.glReadPixels(0, 0, 512, 512, 0x1907, 0x1401, data)
            assert gl.glGetError() == 0, 'Preview OpenGL error'
            output = Path(__file__).resolve().parents[1] / 'build/clouds-preview.ppm'
            output.parent.mkdir(exist_ok=True)
            rows = [bytes(data[y*512*3:(y+1)*512*3]) for y in reversed(range(512))]
            output.write_bytes(b'P6\n512 512\n255\n' + b''.join(rows))
            print('Synthetic cloud preview (not Minecraft):', output)
        print('All offscreen checks passed. Minecraft validation is still required.')
    finally:
        for program in programs.values():
            gl.glDeleteProgram(program)
        driver.close()


if __name__ == '__main__':
    main()

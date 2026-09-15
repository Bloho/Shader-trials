#!/usr/bin/env python3
"""Validate loader includes/contracts; optionally compile/link with macOS OpenGL.

Needs Python 3 and clang. --driver requires macOS GPU access. This is not a
replacement for loading the pack in Minecraft (Iris applies additional patches).
"""
from pathlib import Path
import argparse
import ctypes as C
import re
import subprocess
import sys
from generate import SHADERS, PROGRAMS, WORLDS, generated_files


def expand(path, stack=()):
    path = path.resolve()
    if not path.is_relative_to(SHADERS.resolve()):
        raise AssertionError(f'Include escapes shaderpack: {path}')
    if path in stack:
        raise AssertionError(f'Include cycle: {stack + (path,)}')
    source = path.read_text()
    def replace(match):
        name = match.group(1)
        target = SHADERS / name[1:] if name.startswith('/') else path.parent / name
        return expand(target, stack + (path,))
    return re.sub(r'^\s*#include\s+"([^"]+)"\s*$', replace, source, flags=re.M)


def preprocess(path):
    source = expand(path)
    assert source.startswith('#version 120\n'), path
    assert source.count('#version') == 1, path
    # Only the C-style preprocessor runs; GLSL itself is compiled by the driver.
    result = subprocess.run(['clang', '-E', '-P', '-C', '-x', 'c', '-'],
                            input=source.replace('#version 120', '', 1),
                            capture_output=True, text=True, check=True)
    return '#version 120\n' + result.stdout


def declarations(source, qualifier):
    source = re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)
    return {name: kind for kind, name in re.findall(
        rf'\b{qualifier}\s+(\w+)\s+(\w+)\s*;', source)}


class Driver:
    def __init__(self):
        if sys.platform != 'darwin':
            raise RuntimeError('--driver currently uses macOS CGL')
        self.gl = C.CDLL('/System/Library/Frameworks/OpenGL.framework/OpenGL')
        self.bind('CGLChoosePixelFormat', C.c_int, C.POINTER(C.c_int), C.POINTER(C.c_void_p), C.POINTER(C.c_int))
        self.bind('CGLCreateContext', C.c_int, C.c_void_p, C.c_void_p, C.POINTER(C.c_void_p))
        self.bind('CGLSetCurrentContext', C.c_int, C.c_void_p)
        self.bind('CGLDestroyContext', C.c_int, C.c_void_p)
        self.bind('CGLDestroyPixelFormat', C.c_int, C.c_void_p)
        fmt, count = C.c_void_p(), C.c_int()
        code = self.gl.CGLChoosePixelFormat((C.c_int * 1)(0), C.byref(fmt), C.byref(count))
        if code:
            raise RuntimeError(f'CGL pixel format error {code}; GPU access may be sandboxed')
        self.context = C.c_void_p()
        code = self.gl.CGLCreateContext(fmt, None, C.byref(self.context))
        self.gl.CGLDestroyPixelFormat(fmt)
        if code:
            raise RuntimeError(f'CGL context error {code}')
        assert self.gl.CGLSetCurrentContext(self.context) == 0
        self.bind('glGetString', C.c_char_p, C.c_uint)
        self.bind('glGetError', C.c_uint)
        self.bind('glCreateShader', C.c_uint, C.c_uint)
        self.bind('glShaderSource', None, C.c_uint, C.c_int, C.POINTER(C.c_char_p), C.POINTER(C.c_int))
        self.bind('glCompileShader', None, C.c_uint)
        self.bind('glGetShaderiv', None, C.c_uint, C.c_uint, C.POINTER(C.c_int))
        self.bind('glGetShaderInfoLog', None, C.c_uint, C.c_int, C.POINTER(C.c_int), C.c_char_p)
        self.bind('glCreateProgram', C.c_uint)
        self.bind('glAttachShader', None, C.c_uint, C.c_uint)
        self.bind('glBindAttribLocation', None, C.c_uint, C.c_uint, C.c_char_p)
        self.bind('glLinkProgram', None, C.c_uint)
        self.bind('glGetProgramiv', None, C.c_uint, C.c_uint, C.POINTER(C.c_int))
        self.bind('glGetProgramInfoLog', None, C.c_uint, C.c_int, C.POINTER(C.c_int), C.c_char_p)
        self.bind('glDeleteShader', None, C.c_uint)
        self.bind('glDeleteProgram', None, C.c_uint)
        print('Driver:', self.gl.glGetString(0x1F02).decode(), '/', self.gl.glGetString(0x1F01).decode())

    def bind(self, name, result, *args):
        fn = getattr(self.gl, name)
        fn.restype, fn.argtypes = result, list(args)
        return fn

    def program(self, vertex, fragment):
        gl = self.gl
        shaders = []
        for stage, text in [(0x8B31, vertex), (0x8B30, fragment)]:
            shader = gl.glCreateShader(stage)
            source = C.c_char_p(text.encode())
            gl.glShaderSource(shader, 1, C.byref(source), None)
            gl.glCompileShader(shader)
            status = C.c_int()
            gl.glGetShaderiv(shader, 0x8B81, C.byref(status))
            log = C.create_string_buffer(16384)
            gl.glGetShaderInfoLog(shader, len(log), None, log)
            if not status.value:
                raise AssertionError(log.value.decode())
            if log.value.strip():
                print('Compiler:', log.value.decode().strip())
            shaders.append(shader)
        program = gl.glCreateProgram()
        gl.glBindAttribLocation(program, 10, b'mc_Entity')
        for shader in shaders:
            gl.glAttachShader(program, shader)
        gl.glLinkProgram(program)
        status = C.c_int()
        gl.glGetProgramiv(program, 0x8B82, C.byref(status))
        log = C.create_string_buffer(16384)
        gl.glGetProgramInfoLog(program, len(log), None, log)
        if not status.value:
            raise AssertionError(log.value.decode())
        for shader in shaders:
            gl.glDeleteShader(shader)
        assert gl.glGetError() == 0, 'GL error during compile/link'
        return program

    def close(self):
        self.gl.CGLSetCurrentContext(None)
        self.gl.CGLDestroyContext(self.context)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--driver', action='store_true')
    args = parser.parse_args()
    for path, text in generated_files():
        assert path.read_text() == text, f'Stale generated file: {path}'
    expected = {p for p, _ in generated_files() if p.suffix in ('.vsh', '.fsh')}
    actual = {p for world in WORLDS for p in (SHADERS / world).glob('*.*')
              if p.suffix in ('.vsh', '.fsh')}
    assert actual == expected, f'Unexpected entry points: {actual ^ expected}'
    driver = Driver() if args.driver else None
    count = 0
    try:
        for vp in sorted(p for p in expected if p.suffix == '.vsh'):
            fp = vp.with_suffix('.fsh')
            vertex, fragment = preprocess(vp), preprocess(fp)
            assert declarations(vertex, 'varying') == declarations(fragment, 'varying'), vp
            vu, fu = declarations(vertex, 'uniform'), declarations(fragment, 'uniform')
            for name in vu.keys() & fu.keys():
                assert vu[name] == fu[name], (vp, name)
            outputs = {int(i) for i in re.findall(r'gl_FragData\[(\d+)\]\s*=', fragment)}
            if vp.stem == 'final':
                assert not outputs and 'gl_FragColor =' in fragment, fp
            else:
                targets = re.findall(r'/\* DRAWBUFFERS:(\d+) \*/', fragment)
                assert len(targets) == 1 and outputs == set(range(len(targets[0]))), fp
                assert set(targets[0]) <= set('0123'), fp
            if vp.stem.startswith('gbuffers_'):
                assert not any(n.startswith('colortex') for n in fu), 'Gbuffer feedback loop'
            if driver:
                try:
                    program = driver.program(vertex, fragment)
                    driver.gl.glDeleteProgram(program)
                except Exception as error:
                    raise AssertionError(f'{vp.relative_to(SHADERS)}: {error}') from error
            count += 1
    finally:
        if driver:
            driver.close()
    print(f'PASS: {count} program pairs; includes, varyings, uniforms, outputs, world entry points')
    print('PASS: driver compilation/linking' if driver else 'Driver compilation not requested')


if __name__ == '__main__':
    main()

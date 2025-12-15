from __future__ import annotations


def math_floor_def() -> str:
    return """
    fn floor (x:f64) i64 {
        xi:i64 = x*i64
        ::if(and(ltz(x) ne(x xi*f64)):sub(xi 1) true:xi)
    }
    """


def math_mod2pi_def() -> str:
    return """
    fn mod-2pi (theta:f64) f64 {
        two-pi:f64 = 6.283185307179586
        quot:i64 = floor(div(theta two-pi))
        ::sub(theta mul(two-pi quot*f64))
    }
    """


def math_modpi_def() -> str:
    return """
    fn mod-pi (theta:f64) f64 {
        pi:f64 = 3.141592653589793
        two-pi:f64 = 6.283185307179586
        quot:i64 = floor(div(add(theta pi) two-pi))
        ::sub(theta mul(two-pi quot*f64))
    }
    """


def math_abs_def() -> str:
    return """
    fn abs (x:f64) f64 {
        bit63:u64 = 9223372036854775807 // sub(pow(2 63) 1), clear sign bit
        b:u64
        memcpy(b<&> x<&> sizeof(b))
        memcpy(x<&> b-and(b bit63)<&> sizeof(x))
        ::x
    }
    """


def math_sin_def() -> str:
    return """
    fn sin (theta:f64) f64 {
        pi:f64 = 3.141592653589793
        pi2:f64 = pow(pi 2.0)
        new-theta:f64 = mod-pi(theta)
        abs-theta:f64 = if(ltz(new-theta):neg(new-theta) true:new-theta)
        quad-approx:f64 = sub(div(4.0 pi) div(mul(4.0 abs(new-theta)) pi2))
        ::mul(new-theta quad-approx)
    } 
    """


def math1_types_def() -> str:
    return """
    type point:i64
    type line {x:i32}
    type surface:u64
    """


def math2_types_def() -> str:
    return """
    type plane {x:i32 y:i32}
    """


def math3_types_def() -> str:
    return """
    type normal {dx:i32 dy:i32 dz:i32}
    """


def math4_types_def() -> str:
    return """
    type space {x:i64 y:u64 z:i64}
    type surface:u64
    type volume:u64
    """


def math5_types_def() -> str:
    return """
    type form {vol:u64}
    """


def io1_types_def() -> str:
    return """
    type socket {raw:u32}
    """


def qstd1_types_def() -> str:
    return """
    type @bell_t {@source:@bool @target:@bool}
    """

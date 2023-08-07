#########################
#  MACRO definitions    # 
#########################

class MACROS:
    SOLIDITY_FNAME  = ""
    THEOREM_FNAME   = ""
    TRACE_FNAME     = ""
    STORAGE         = "./temp_solc_storage.json"
    ABI             = "./temp_solc_abi.json"
    AST             = "./temp_solc_ast.json"
    RUNTIME         = "./temp_solc_runtime.json"
    DEVDOC          = "./temp_solc_devdoc.json"
    ESSENTIAL       = "./temp_essential.txt"
    BOOGIE          = ""  
    CONTRACT_NAME   = ""
    FUNCTION_NAME   = ""
    VAR_TYPES       = {}
    NUM_TYPE        = ""
    INVARIANTS      = {}
    ALL_VARS        = {"tx_origin": ""}
    DEF_VARS        = {}
    DECL_VARS       = {}
    DECL_SUBS       = {}



    PREAMBLE_COMMON = """type address = int;
type bytes32 = int;
type uint8 = int;
const TwoE16 : uint256;
axiom TwoE16 == TwoE8 * TwoE8; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 * TwoE8;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b-TwoE256);
axiom (forall a,b: uint256 :: evmadd(a,b)>=a ==> evmadd(a,b) == a+b);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a>=b ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a<b ==> evmsub(a,b) == a-b+TwoE256);
axiom (forall a,b: uint256 :: evmsub(a,b)<=a ==> evmsub(a,b) == a-b);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmdiv(evmmul(a,b),a)==b ==> evmmul(a,b) == a*b);

function evmmod(a,b:uint256) returns (uint256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: Zero<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));

function nondet() returns (uint256);

"""

    PREAMBLE_INT    =   """type uint256 = int;
const Zero : uint256;
axiom Zero == 0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768; 

""" + PREAMBLE_COMMON

    PREAMBLE_REAL    =   """type uint256 = real;
const Zero : uint256;
axiom Zero == 0.0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768.0; 

function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 

""" + PREAMBLE_COMMON



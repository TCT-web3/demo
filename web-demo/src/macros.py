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


    PREAMBLE_INT    =   """type address = int;
type uint256 = int;
const TwoE16 : uint256;
axiom TwoE16 == 65536; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b-TwoE256);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> evmsub(a,b) == a-b+TwoE256);

function evmmod(a,b:uint256) returns (uint256);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmmul(a,b) == a*b);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: 0<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));    

procedure straightline_code ()
{  
    var tx_origin: address;
    var BLOCKTIME: uint256;
"""

    PREAMBLE_REAL    =   """type address = int;
type uint256 = real;
const TwoE16 : uint256;
axiom TwoE16 == 65536.0; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768.0;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b-TwoE256);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> evmsub(a,b) == a-b+TwoE256);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmmul(a,b) == a*b);
function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 

function evmmod(a,b:uint256) returns (uint256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: 0<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));    

procedure straightline_code ()
{  
    var tx_origin: address;
    var BLOCKTIME: uint256;
"""






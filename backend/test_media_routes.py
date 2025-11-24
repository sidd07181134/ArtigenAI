"""
Quick test script to verify media transcription routes are registered.
Run this to check if routes are accessible before testing in the frontend.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

def test_routes():
    """Test if media transcription routes are registered"""
    print("Checking for media transcription routes...")
    print("-" * 60)
    
    # Get all routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            if 'media' in route.path.lower():
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else []
                })
    
    if routes:
        print(f"✓ Found {len(routes)} media transcription route(s):")
        for route in routes:
            methods = ', '.join(route['methods'])
            print(f"  {methods:8} {route['path']}")
    else:
        print("✗ No media transcription routes found!")
        print("\nPossible issues:")
        print("  1. Router not imported in main.py")
        print("  2. Router not included with app.include_router()")
        print("  3. Import error preventing router from loading")
        print("\nChecking router import...")
        
        try:
            from app.api import media_transcription
            print(f"  ✓ Router imported successfully")
            print(f"  ✓ Router prefix: {media_transcription.router.prefix}")
            print(f"  ✓ Router has {len(media_transcription.router.routes)} route(s)")
            for r in media_transcription.router.routes:
                if hasattr(r, 'path') and hasattr(r, 'methods'):
                    print(f"    - {list(r.methods)} {r.path}")
        except Exception as e:
            print(f"  ✗ Failed to import router: {e}")
            return False
    
    print("-" * 60)
    
    # Check OpenAPI schema
    try:
        openapi = app.openapi()
        media_paths = {k: v for k, v in openapi.get('paths', {}).items() if 'media' in k}
        if media_paths:
            print(f"✓ OpenAPI schema includes {len(media_paths)} media path(s):")
            for path in media_paths.keys():
                print(f"  {path}")
        else:
            print("✗ OpenAPI schema does not include media paths")
    except Exception as e:
        print(f"✗ Failed to get OpenAPI schema: {e}")
    
    return len(routes) > 0

if __name__ == "__main__":
    success = test_routes()
    sys.exit(0 if success else 1)


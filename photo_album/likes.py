from typing import Optional

from fastapi import Request, Depends
from fastapi.responses import HTMLResponse

from photo_album.clients.firestore import db_client
from photo_album.logger import log
from photo_album.routes import router, templates
from photo_album.auth import get_user


@router.post("/likes/{album}/{asset}")
async def likes(request: Request, album: str, asset: str, user: Optional[dict] = Depends(get_user)):

    if user is None:
        # User is not authenticated, redirect to login
        request.session['origin'] = "/"
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )

    document_id = f"{album}-{asset}"
    likes_collection = db_client.collection("likes")
    asset_doc_ref = likes_collection.document(document_id)

    try:
        asset_doc = asset_doc_ref.get()
        like_data = asset_doc.to_dict() if asset_doc.exists else {}

        if not like_data:
            like_data = {"Asset": asset, "Album": album, "Likes": 0, "Users": []}

        like_data["Likes"] += 1
        if user["email"] not in like_data["Users"]:
            like_data["Users"].append(user["email"])

        asset_doc_ref.set(like_data, merge=True)  # merge avoids field overwrite

        return HTMLResponse("<i class=\"fa-solid fa-heart\"></i>")

    except Exception as e:
        log.error(f"Error updating likes for asset [{asset}]: {e}")
        return templates.TemplateResponse(
            status_code=500,
            name="error.html",
            context={
                "site_name": "Photo Albums",
                "page_title": "Error",
                "page_description": "Alex's Photo & Video Albums",
                "error_msg": str(e),
                "request": request,
            }
        )

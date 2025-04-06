from flask import request
from flask_restx import Namespace, Resource, fields
from models import db, Video
from logger import log_info, log_error, log_debug

video_ns = Namespace('video', description='Добавление видео')

video_model = video_ns.model('Video', {
    'link': fields.String(required=True, description='Ссылка на видео'),
    'title': fields.String(required=True, description='Название видео'),
    'description': fields.String(description='Описание видео'),
    'hashtag': fields.String(description='Хэштег видео')
})

@video_ns.route('/add_video')
class AddVideo(Resource):
    @video_ns.expect(video_model)
    @video_ns.response(201, 'Video added successfully')
    @video_ns.response(400, 'Missing required fields')
    def post(self):
        data = request.json
        link = data.get('link')
        title = data.get('title')
        description = data.get('description', '')
        hashtag = data.get('hashtag', '')

        if not link or not title:
            log_error("Missing link or title in video request")
            return {'message': 'Link and title are required'}, 400

        try:
            new_video = Video(link=link, title=title, description=description, hashtag=hashtag)
            db.session.add(new_video)
            db.session.commit()
            log_info(f"Video '{title}' added successfully")
            return new_video.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to add video: {str(e)}")
            return {'message': 'Database error'}, 500

@video_ns.route('/videos')
class VideoList(Resource):
    @video_ns.doc('list_videos')
    def get(self):
        try:
            videos = Video.query.all()
            log_info(f"Retrieved {len(videos)} videos successfully")
            return [video.to_dict() for video in videos], 200
        except Exception as e:
            log_error(f"Error retrieving videos: {str(e)}")
            return {'message': 'Internal server error'}, 500

@video_ns.route('/videos/<int:video_id>')
class VideoResource(Resource):
    @video_ns.doc('delete_video', responses={200: 'Video deleted successfully', 404: 'Video not found', 500: 'Database error'})
    def delete(self, video_id):
        try:
            video = Video.query.get(video_id)
            if not video:
                log_error(f"Video with id {video_id} not found")
                return {'message': 'Video not found'}, 404
            db.session.delete(video)
            db.session.commit()
            log_info(f"Video with id {video_id} deleted successfully")
            return {'message': 'Video deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to delete video with id {video_id}: {str(e)}")
            return {'message': 'Database error'}, 500

    @video_ns.expect(video_model, validate=True)
    @video_ns.doc('update_video', responses={200: 'Video updated successfully', 404: 'Video not found', 500: 'Database error'})
    def put(self, video_id):
        try:
            video = Video.query.get(video_id)
            if not video:
                log_error(f"Video with id {video_id} not found for update")
                return {'message': 'Video not found'}, 404

            data = request.json
            video.link = data.get('link', video.link)
            video.title = data.get('title', video.title)
            video.description = data.get('description', video.description)
            video.hashtag = data.get('hashtag', video.hashtag)

            db.session.commit()
            log_info(f"Video with id {video_id} updated successfully")
            return video.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            log_error(f"Failed to update video with id {video_id}: {str(e)}")
            return {'message': 'Database error'}, 500
interface CourseCardProps {
  title: string;
  description: string;
  level: string;
  lessons: number;
  imageUrl: string;
}

export default function CourseCard({ title, description, level, lessons, imageUrl }: CourseCardProps) {
  return (
    <div className="card group relative flex flex-col overflow-hidden">
      <div className="aspect-h-3 aspect-w-4 bg-gray-200 sm:aspect-none sm:h-48">
        <img
          src={imageUrl}
          alt={title}
          className="h-full w-full object-cover object-center sm:h-full sm:w-full"
        />
      </div>
      <div className="flex flex-1 flex-col space-y-2 p-4">
        <h3 className="text-lg font-medium text-gray-900">
          <a href="#">
            <span aria-hidden="true" className="absolute inset-0" />
            {title}
          </a>
        </h3>
        <p className="text-sm text-gray-500">{description}</p>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800">
              {level}
            </span>
            <span className="text-sm text-gray-500">{lessons} lessons</span>
          </div>
          <button className="btn btn-primary text-sm">Start Learning</button>
        </div>
      </div>
    </div>
  );
} 